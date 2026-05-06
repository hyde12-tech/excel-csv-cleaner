# CustomTkinter 移行 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** tkinter/ttk で実装された GUI を CustomTkinter に移行し、タブ統合レイアウトで1画面化する

**Architecture:** main.py に CTkTabview を設置して2つの処理画面をタブとして統合する。gui_single.py と gui_merge.py はウィンドウベースからフレームベースに変更し、CTk ウィジェットに置き換える。processor.py と file_io.py は変更しない。

**Tech Stack:** Python, customtkinter>=5.2.0, tkinter（messagebox/filedialog は引き続き使用）

---

### Task 1: customtkinter のインストールと requirements.txt 更新

**Files:**
- Modify: `excel-csv-cleaner/requirements.txt`

- [ ] **Step 1: customtkinter をインストールする**

```
pip install customtkinter
```
Expected: `Successfully installed customtkinter-x.x.x`

- [ ] **Step 2: requirements.txt に追加する**

`requirements.txt` の末尾に以下を追加:
```
customtkinter>=5.2.0
```

- [ ] **Step 3: 既存のテストが引き続き通ることを確認する**

```
cd excel-csv-cleaner
python -m pytest tests/ -v
```
Expected: 全テスト PASS（GUI に関係するテストはないため変更なし）

- [ ] **Step 4: コミット**

```bash
git add requirements.txt
git commit -m "chore: add customtkinter dependency"
```

---

### Task 2: main.py を CTk + CTkTabview に移行する

**Files:**
- Modify: `excel-csv-cleaner/main.py`

- [ ] **Step 1: main.py を以下の内容に書き換える**

```python
import customtkinter as ctk
from gui_single import SingleProcessFrame
from gui_merge import MergeFrame

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


def main():
    root = ctk.CTk()
    root.title('Excel/CSV データ整理ツール')
    root.resizable(False, False)

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

- [ ] **Step 2: コミット**

```bash
git add main.py
git commit -m "feat: replace tkinter root with CTk + CTkTabview"
```

---

### Task 3: gui_single.py を CTk ウィジェットに移行する

**Files:**
- Modify: `excel-csv-cleaner/gui_single.py`

- [ ] **Step 1: gui_single.py を以下の内容に書き換える**

```python
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from file_io import read_table, write_table
from processor import dedupe, sort_data, aggregate


class SingleProcessFrame:
    def __init__(self, parent):
        self.parent = parent
        self.file_path = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        # ファイル選択
        ctk.CTkLabel(self.parent, text='ファイル選択', anchor='w').pack(
            fill='x', padx=10, pady=(10, 0))
        file_frame = ctk.CTkFrame(self.parent)
        file_frame.pack(fill='x', padx=10, pady=(4, 8))
        self._file_entry = ctk.CTkEntry(
            file_frame, textvariable=self.file_path, width=300, state='disabled')
        self._file_entry.pack(side='left', padx=(10, 5), pady=8)
        ctk.CTkButton(
            file_frame, text='ファイルを選択',
            command=self._select_file, width=120).pack(side='left', padx=5)

        # 処理オプション
        ctk.CTkLabel(self.parent, text='処理を選択', anchor='w').pack(
            fill='x', padx=10, pady=(0, 0))
        opt = ctk.CTkFrame(self.parent)
        opt.pack(fill='x', padx=10, pady=(4, 8))

        # 重複削除
        self.do_dedupe = tk.BooleanVar()
        ctk.CTkCheckBox(opt, text='重複データを削除', variable=self.do_dedupe).grid(
            row=0, column=0, sticky='w', padx=10, pady=8)

        # 並び替え
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

        # 集計
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

        # 実行ボタン
        ctk.CTkButton(
            self.parent, text='実行する',
            command=self._run, width=200).pack(pady=12)

    def _select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[('Excel/CSV', '*.xlsx *.csv'),
                       ('Excel', '*.xlsx'), ('CSV', '*.csv')]
        )
        if not path:
            return
        # disabled 状態では textvariable 経由で値を更新できないため一時的に normal にする
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

    def _run(self):
        path = self.file_path.get()
        if not path:
            messagebox.showwarning('警告', 'ファイルを選択してください')
            return
        if not any([self.do_dedupe.get(), self.do_sort.get(), self.do_agg.get()]):
            messagebox.showwarning('警告', '処理を1つ以上選択してください')
            return
        try:
            df = read_table(path)

            if self.do_dedupe.get():
                df = dedupe(df)

            if self.do_sort.get():
                col = self.sort_col_cb.get()
                if col:
                    asc = self.sort_order.get() == '昇順'
                    df = sort_data(df, columns=[col], ascending=[asc])

            if self.do_agg.get():
                group = self.agg_group_cb.get()
                value = self.agg_value_cb.get()
                method_map = {'合計': 'sum', '平均': 'mean', '件数': 'count'}
                if group and value:
                    df = aggregate(df, group_by=group, value_col=value,
                                   method=method_map[self.agg_method_cb.get()])

            save_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel', '*.xlsx'), ('CSV', '*.csv')],
                title='保存先を選択'
            )
            if not save_path:
                return
            write_table(df, save_path)
            messagebox.showinfo('完了', f'保存しました！\n{save_path}')
        except Exception as e:
            messagebox.showerror('エラー', f'処理中にエラーが発生しました:\n{e}')
```

- [ ] **Step 2: コミット**

```bash
git add gui_single.py
git commit -m "feat: migrate SingleProcessFrame to CustomTkinter"
```

---

### Task 4: gui_merge.py を CTk ウィジェットに移行する

**Files:**
- Modify: `excel-csv-cleaner/gui_merge.py`

- [ ] **Step 1: gui_merge.py を以下の内容に書き換える**

```python
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from file_io import read_table, write_table
from processor import merge_files


class MergeFrame:
    def __init__(self, parent):
        self.parent = parent
        self.file_paths = []
        self._selected_index = None
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self.parent, text='統合するファイル（2つ以上）', anchor='w').pack(
            fill='x', padx=10, pady=(10, 0))

        self.scroll_frame = ctk.CTkScrollableFrame(self.parent, height=150)
        self.scroll_frame.pack(fill='x', padx=10, pady=(4, 8))

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

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            filetypes=[('Excel/CSV', '*.xlsx *.csv'),
                       ('Excel', '*.xlsx'), ('CSV', '*.csv')]
        )
        for path in paths:
            if path not in self.file_paths:
                self.file_paths.append(path)
        self._rebuild_list()

    def _rebuild_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._selected_index = None
        for i, path in enumerate(self.file_paths):
            name = path.replace('\\', '/').split('/')[-1]
            label = ctk.CTkLabel(self.scroll_frame, text=name, anchor='w', cursor='hand2')
            label.pack(fill='x', padx=4, pady=2)
            label.bind('<Button-1>', lambda e, idx=i: self._select_item(idx))

    def _select_item(self, index):
        self._selected_index = index
        for i, widget in enumerate(self.scroll_frame.winfo_children()):
            if i == index:
                widget.configure(fg_color=('gray70', 'gray30'))
            else:
                widget.configure(fg_color='transparent')

    def _remove_selected(self):
        if self._selected_index is None:
            return
        self.file_paths.pop(self._selected_index)
        self._rebuild_list()

    def _run(self):
        if len(self.file_paths) < 2:
            messagebox.showwarning('警告', 'ファイルを2つ以上追加してください')
            return
        try:
            dfs = [read_table(p) for p in self.file_paths]
            merged = merge_files(dfs)

            save_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel', '*.xlsx'), ('CSV', '*.csv')],
                title='保存先を選択'
            )
            if not save_path:
                return
            write_table(merged, save_path)
            messagebox.showinfo('完了',
                f'統合完了！\n{len(self.file_paths)}ファイル → {len(merged)}行\n{save_path}')
        except Exception as e:
            messagebox.showerror('エラー', f'処理中にエラーが発生しました:\n{e}')
```

- [ ] **Step 2: コミット**

```bash
git add gui_merge.py
git commit -m "feat: migrate MergeFrame to CustomTkinter"
```

---

### Task 5: 動作確認・テスト・最終コミット

**Files:**
- 変更なし

- [ ] **Step 1: 既存テストが全て通ることを確認する**

```
cd excel-csv-cleaner
python -m pytest tests/ -v
```
Expected: 全テスト PASS

- [ ] **Step 2: GUI を手動で起動して動作確認する**

```
cd excel-csv-cleaner
python main.py
```

確認項目：
1. ウィンドウが起動してタブが2つ表示される
2. 「📄 単体ファイル処理」タブでExcel/CSVを選択できる
3. 重複削除・並び替え・集計を実行して保存できる
4. 「📑 複数ファイル統合」タブでファイルを複数追加できる
5. ファイルをクリックで選択→削除できる
6. 統合して保存できる
7. ダーク/ライトモードが OS の設定に連動している

- [ ] **Step 3: 最終コミット＆プッシュ**

```bash
git add .
git commit -m "feat: complete CustomTkinter migration with tab layout"
git push
```
