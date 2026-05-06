# ドラッグ＆ドロップ＋ウィンドウリサイズ 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ファイルのドラッグ＆ドロップ読み込みとウィンドウの任意サイズ変更を追加する

**Architecture:** tkinterdnd2 を ctk.CTk と組み合わせた `_CTkDnD` クラスをルートウィンドウとして使う。ドロップゾーンは各タブの既存フレーム（file_frame / scroll_frame）に直接登録し、DragEnter/Leave/Drop イベントで青枠フィードバックと読み込みを行う。

**Tech Stack:** Python, customtkinter>=5.2.0, tkinterdnd2, tkinter（messagebox/filedialog）, PyInstaller

---

### Task 1: tkinterdnd2 のインストールと requirements.txt 更新

**Files:**
- Modify: `excel-csv-cleaner/requirements.txt`

- [ ] **Step 1: tkinterdnd2 をインストールする**

```
pip install tkinterdnd2
```
Expected: `Successfully installed tkinterdnd2-x.x.x`

- [ ] **Step 2: requirements.txt に追加する**

`requirements.txt` を以下の内容にする:
```
pandas
openpyxl
pytest
customtkinter>=5.2.0
tkinterdnd2
```

- [ ] **Step 3: 既存テストが引き続き通ることを確認する**

```
cd excel-csv-cleaner
python -m pytest tests/ -v
```
Expected: 17 passed

- [ ] **Step 4: コミット**

```bash
git add requirements.txt
git commit -m "chore: add tkinterdnd2 dependency"
```

---

### Task 2: main.py に TkinterDnD 統合とリサイズ設定を追加する

**Files:**
- Modify: `excel-csv-cleaner/main.py`

- [ ] **Step 1: main.py を以下の内容に書き換える**

```python
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from gui_single import SingleProcessFrame
from gui_merge import MergeFrame

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class _CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    """ctk.CTk にドラッグ＆ドロップ機能を追加したルートウィンドウ"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


def main():
    root = _CTkDnD()
    root.title('Excel/CSV データ整理ツール')
    root.resizable(True, True)
    root.minsize(500, 400)

    ctk.CTkLabel(root, text='📊 Excel/CSV データ整理ツール',
                 font=ctk.CTkFont(size=16, weight='bold')).pack(pady=(20, 10))

    tabview = ctk.CTkTabview(root)
    tabview.pack(padx=20, pady=(0, 20), fill='both', expand=True)

    tabview.add('📄 単体ファイル処理')
    tabview.add('📑 複数ファイル統合')

    SingleProcessFrame(tabview.tab('📄 単体ファイル処理'))
    MergeFrame(tabview.tab('📑 複数ファイル統合'))

    root.mainloop()


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: 起動確認**

```
cd excel-csv-cleaner
python main.py
```
Expected: ウィンドウが起動し、四隅ドラッグでサイズ変更できる（ドロップは Task 3・4 完了後に動作）

- [ ] **Step 3: コミット**

```bash
git add main.py
git commit -m "feat: add TkinterDnD root and enable window resize"
```

---

### Task 3: gui_single.py にドロップゾーンを追加する

**Files:**
- Modify: `excel-csv-cleaner/gui_single.py`

- [ ] **Step 1: gui_single.py の `_build_ui` と `_select_file` を以下のように変更する**

`_build_ui` のファイル選択部分（`file_frame` 作成から CTkButton まで）を以下に置き換える:

```python
    def _build_ui(self):
        # ファイル選択
        ctk.CTkLabel(self.parent, text='ファイル選択', anchor='w').pack(
            fill='x', padx=10, pady=(10, 0))
        self.file_frame = ctk.CTkFrame(self.parent)
        self.file_frame.pack(fill='x', padx=10, pady=(4, 8))
        self._file_entry = ctk.CTkEntry(
            self.file_frame, textvariable=self.file_path, width=300, state='disabled')
        self._file_entry.pack(side='left', padx=(10, 5), pady=8)
        ctk.CTkButton(
            self.file_frame, text='ファイルを選択',
            command=self._select_file, width=120).pack(side='left', padx=5)

        # ドラッグ＆ドロップの設定
        from tkinterdnd2 import DND_FILES
        self.file_frame.drop_target_register(DND_FILES)
        self.file_frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.file_frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        self.file_frame.dnd_bind('<<Drop>>', self._on_drop)

        # 処理オプション（以降は変更なし）
        ctk.CTkLabel(self.parent, text='処理を選択', anchor='w').pack(
            fill='x', padx=10, pady=(0, 0))
        opt = ctk.CTkFrame(self.parent)
        opt.pack(fill='x', padx=10, pady=(4, 8))

        self.do_dedupe = tk.BooleanVar()
        ctk.CTkCheckBox(opt, text='重複データを削除', variable=self.do_dedupe).grid(
            row=0, column=0, sticky='w', padx=10, pady=8)

        self.do_sort = tk.BooleanVar()
        ctk.CTkCheckBox(opt, text='並び替え', variable=self.do_sort).grid(
            row=1, column=0, sticky='w', padx=10, pady=4)
        ctk.CTkLabel(opt, text='列:').grid(row=1, column=1, padx=4)
        self.sort_col_cb = ctk.CTkComboBox(opt, width=120, values=[])
        self.sort_col_cb.grid(row=1, column=2, padx=4)
        self.sort_order = tk.StringVar(value='昇順')
        ctk.CTkRadioButton(
            opt, text='昇順', variable=self.sort_order, value='昇順').grid(
            row=1, column=3, padx=4)
        ctk.CTkRadioButton(
            opt, text='降順', variable=self.sort_order, value='降順').grid(
            row=1, column=4, padx=4)

        self.do_agg = tk.BooleanVar()
        ctk.CTkCheckBox(opt, text='集計', variable=self.do_agg).grid(
            row=2, column=0, sticky='w', padx=10, pady=4)
        ctk.CTkLabel(opt, text='グループ:').grid(row=2, column=1, padx=4)
        self.agg_group_cb = ctk.CTkComboBox(opt, width=100, values=[])
        self.agg_group_cb.grid(row=2, column=2, padx=4)
        ctk.CTkLabel(opt, text='集計列:').grid(row=2, column=3, padx=4)
        self.agg_value_cb = ctk.CTkComboBox(opt, width=100, values=[])
        self.agg_value_cb.grid(row=2, column=4, padx=4)

        ctk.CTkLabel(opt, text='集計方法:').grid(row=3, column=1, padx=4, pady=(0, 10))
        self.agg_method_cb = ctk.CTkComboBox(
            opt, values=['合計', '平均', '件数'], width=80)
        self.agg_method_cb.set('合計')
        self.agg_method_cb.grid(row=3, column=2, padx=4)

        ctk.CTkButton(
            self.parent, text='実行する',
            command=self._run, width=200).pack(pady=12)
```

- [ ] **Step 2: ドロップイベントハンドラと `_load_file` ヘルパーを追加する**

`_select_file` メソッドの直後に以下を追加する:

```python
    def _on_drag_enter(self, event):
        self.file_frame.configure(border_width=2, border_color='#1f6feb')

    def _on_drag_leave(self, event):
        self.file_frame.configure(border_width=0)

    def _on_drop(self, event):
        self.file_frame.configure(border_width=0)
        paths = self.file_frame.tk.splitlist(event.data)
        if not paths:
            return
        path = paths[0]
        if not path.lower().endswith(('.xlsx', '.csv')):
            return
        self._load_file(path)

    def _load_file(self, path):
        self._file_entry.configure(state='normal')
        self.file_path.set(path)
        self._file_entry.configure(state='disabled')
        try:
            df = read_table(path)
            cols = list(df.columns)
            self.sort_col_cb.configure(values=cols)
            self.agg_group_cb.configure(values=cols)
            self.agg_value_cb.configure(values=cols)
            if cols:
                self.sort_col_cb.set(cols[0])
                self.agg_group_cb.set(cols[0])
                self.agg_value_cb.set(cols[-1])
        except Exception as e:
            messagebox.showerror('エラー', f'ファイルを読み込めませんでした:\n{e}')
```

- [ ] **Step 3: `_select_file` を `_load_file` を使う形にリファクタする**

```python
    def _select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[('Excel/CSV', '*.xlsx *.csv'),
                       ('Excel', '*.xlsx'), ('CSV', '*.csv')]
        )
        if not path:
            return
        self._load_file(path)
```

- [ ] **Step 4: コミット**

```bash
git add gui_single.py
git commit -m "feat: add drag-and-drop to single file tab"
```

---

### Task 4: gui_merge.py にドロップゾーンを追加する

**Files:**
- Modify: `excel-csv-cleaner/gui_merge.py`

- [ ] **Step 1: `_build_ui` の scroll_frame 作成部分にドロップ設定を追加する**

`_build_ui` を以下の内容に置き換える:

```python
    def _build_ui(self):
        ctk.CTkLabel(self.parent, text='統合するファイル（2つ以上）', anchor='w').pack(
            fill='x', padx=10, pady=(10, 0))

        self.scroll_frame = ctk.CTkScrollableFrame(self.parent, height=150)
        self.scroll_frame.pack(fill='x', padx=10, pady=(4, 8))

        # ドラッグ＆ドロップの設定
        from tkinterdnd2 import DND_FILES
        self.scroll_frame.drop_target_register(DND_FILES)
        self.scroll_frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.scroll_frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        self.scroll_frame.dnd_bind('<<Drop>>', self._on_drop)

        btn_frame = ctk.CTkFrame(self.parent, fg_color='transparent')
        btn_frame.pack(fill='x', padx=10, pady=(0, 8))
        ctk.CTkButton(
            btn_frame, text='ファイルを追加',
            command=self._add_files, width=130).pack(side='left', padx=(0, 8))
        ctk.CTkButton(
            btn_frame, text='選択を削除',
            command=self._remove_selected, width=100,
            fg_color='gray40', hover_color='gray30').pack(side='left')

        ctk.CTkButton(
            self.parent, text='統合する',
            command=self._run, width=200).pack(pady=12)
```

- [ ] **Step 2: ドロップイベントハンドラを追加する**

`_add_files` メソッドの直後に以下を追加する:

```python
    def _on_drag_enter(self, event):
        self.scroll_frame.configure(border_width=2, border_color='#1f6feb')

    def _on_drag_leave(self, event):
        self.scroll_frame.configure(border_width=0)

    def _on_drop(self, event):
        self.scroll_frame.configure(border_width=0)
        paths = self.scroll_frame.tk.splitlist(event.data)
        added = False
        for path in paths:
            if path.lower().endswith(('.xlsx', '.csv')) and path not in self.file_paths:
                self.file_paths.append(path)
                added = True
        if added:
            self._rebuild_list()
```

- [ ] **Step 3: コミット**

```bash
git add gui_merge.py
git commit -m "feat: add drag-and-drop to merge file tab"
```

---

### Task 5: .exe ビルドと動作確認・最終コミット

**Files:**
- 変更なし（ビルド成果物のみ）

- [ ] **Step 1: 既存テストが全て通ることを確認する**

```
cd excel-csv-cleaner
python -m pytest tests/ -v
```
Expected: 17 passed

- [ ] **Step 2: GUI を手動で起動して動作確認する**

```
cd excel-csv-cleaner
python main.py
```

確認項目：
1. ウィンドウが起動する
2. 四隅・端のドラッグでサイズ変更できる
3. 単体タブでファイルをドラッグすると選択エリアが青くなる
4. ドロップするとファイルが読み込まれる（xlsx/csv のみ）
5. 統合タブでファイルをドラッグするとリストエリアが青くなる
6. ドロップするとファイルが一覧に追加される
7. xlsx/csv 以外のファイルは無視される

- [ ] **Step 3: .exe をビルドする**

```
cd excel-csv-cleaner
pyinstaller --noconfirm --onefile --windowed --collect-all customtkinter --collect-all tkinterdnd2 --name "データ整理ツール" main.py
```
Expected: `dist/データ整理ツール.exe` が生成される

- [ ] **Step 4: .exe の動作確認**

`dist/データ整理ツール.exe` をダブルクリックして起動し、Step 2 と同じ確認項目をチェックする。

- [ ] **Step 5: 最終コミット＆プッシュ**

```bash
git add .
git commit -m "feat: add drag-and-drop and window resize, rebuild exe"
git push
```
