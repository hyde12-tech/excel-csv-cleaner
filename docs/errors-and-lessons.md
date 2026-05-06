# 実装中に起きたエラー・ミスの記録

## CustomTkinter 移行（tkinter → CustomTkinter）

### ① CTkEntry の state='disabled' でテキストを更新できない
- **症状**: `state='disabled'` のまま `textvariable` 経由で値を設定しようとしても表示が更新されない
- **解決策**: 一時的に `state='normal'` にしてから値を設定し、再度 `state='disabled'` に戻す
```python
self._file_entry.configure(state='normal')
self.file_path.set(path)
self._file_entry.configure(state='disabled')
```

### ② tk.StringVar / tk.BooleanVar は CTk に置き換えない
- **症状**: スペックレビュアーが「すべて ctk 系に置き換えていない」と誤指摘
- **事実**: CustomTkinter には `StringVar` / `BooleanVar` の代替クラスが存在しない。`tk.StringVar` / `tk.BooleanVar` をそのまま使うのが正しい実装

---

## ドラッグ＆ドロップ（tkinterdnd2 + CustomTkinter）

### ③ tkinterdnd2 と ctk.CTk() の組み合わせ
- **症状**: `tkinterdnd2` は `TkinterDnD.Tk()` をルートウィンドウとして要求するが、`ctk.CTk()` と共存できない
- **解決策**: `ctk.CTk` と `TkinterDnD.DnDWrapper` を多重継承したクラスを作成
```python
class _CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
```

### ④ CTkScrollableFrame のD&Dが動作しない
- **症状**: `scroll_frame.drop_target_register(DND_FILES)` を登録しても、ファイルをドロップしても反応しない
- **根本原因**: `CTkScrollableFrame` の内部に `tk.Canvas` ウィジェットがあり、マウスイベントを Canvas が受け取るため外側フレームには届かない
- **解決策**: `winfo_children()` で内部 Canvas を動的に検索して同じイベントを登録する
```python
self.scroll_frame.drop_target_register(DND_FILES)
self.scroll_frame.dnd_bind('<<Drop>>', self._on_drop)
for child in self.scroll_frame.winfo_children():
    if child.winfo_class() == 'Canvas':
        child.drop_target_register(DND_FILES)
        child.dnd_bind('<<Drop>>', self._on_drop)
        break
```

### ⑤ CTkScrollableFrame に `_canvas` 属性が存在しない
- **症状**: `self.scroll_frame._canvas` にアクセスすると `AttributeError: 'CTkScrollableFrame' object has no attribute '_canvas'` が発生
- **原因**: CustomTkinter のバージョン（5.2.2）によって内部属性名が異なる
- **解決策**: 属性名に依存せず `winfo_children()` + `winfo_class() == 'Canvas'` で動的に検索する（④と同じ対応）

---

## PyInstaller（.exe 化）

### ⑥ tkinterdnd2 を .exe に同梱する方法
- **注意点**: `--collect-data tkinterdnd2` だけでは不十分なことがある
- **正しいコマンド**: `--collect-all tkinterdnd2` を使う
```
pyinstaller --noconfirm --onefile --windowed \
  --collect-all customtkinter \
  --collect-all tkinterdnd2 \
  --name "データ整理ツール" main.py
```

---

## その他

### ⑦ GitHub へのプッシュがネットワークエラー
- **症状**: `fatal: unable to access '...': Could not resolve host: github.com`
- **対応**: セッション内では解決できないので、ユーザーがネット回復後に手動でプッシュする
