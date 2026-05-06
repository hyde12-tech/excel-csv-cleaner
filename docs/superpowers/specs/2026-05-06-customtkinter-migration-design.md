# CustomTkinter 移行 設計書

## 概要

現在 tkinter/ttk で実装されている GUI を CustomTkinter に移行する。
テーマはシステム設定に合わせ、アクセントカラーはブルー。
別ウィンドウで開いていた2つの画面をタブで統合し、1画面に収める。

---

## 決定事項

| 項目 | 内容 |
|---|---|
| ライブラリ | customtkinter |
| テーマ | system（OSのダーク/ライト設定に自動対応） |
| アクセントカラー | blue（CustomTkinterデフォルトブルー） |
| レイアウト | タブ統合（CTkTabview で1画面化） |

---

## 変更するファイル

### `requirements.txt`
- `customtkinter` を追加する

### `main.py`
- `tk.Tk()` → `ctk.CTk()`
- `ttk.Label` → `ctk.CTkLabel`
- `ttk.Button` → `ctk.CTkButton`
- `ttk.Frame` → `ctk.CTkFrame`
- 別ウィンドウを開く2ボタン構成を廃止し、`CTkTabview` を使ったタブ構成に変更
- `SingleProcessWindow` と `MergeWindow` をタブ内に埋め込む形に変更
- `ctk.set_appearance_mode("system")` と `ctk.set_default_color_theme("blue")` を設定

### `gui_single.py`
- `SingleProcessWindow` の `__init__` が `root` だけでなく `parent`（タブのフレーム）を受け取れるよう変更
- `ttk.LabelFrame` → `ctk.CTkFrame`（ラベルは `CTkLabel` で別途配置）
- `ttk.Entry` → `ctk.CTkEntry`
- `ttk.Button` → `ctk.CTkButton`
- `ttk.Checkbutton` → `ctk.CTkCheckBox`
- `ttk.Combobox` → `ctk.CTkComboBox`
- `ttk.Radiobutton` → `ctk.CTkRadioButton`
- `messagebox` / `filedialog` はそのまま維持（CTk版は不要）

### `gui_merge.py`
- `MergeWindow` の `__init__` が `parent`（タブのフレーム）を受け取れるよう変更
- `ttk.LabelFrame` → `ctk.CTkFrame`
- `ttk.Button` → `ctk.CTkButton`
- `tk.Listbox` + `ttk.Scrollbar` → `ctk.CTkScrollableFrame`（スクロール付きフレームにファイル名ラベルを積む）
- `messagebox` / `filedialog` はそのまま維持

---

## 変更しないもの

- `processor.py`（データ処理ロジック）
- `file_io.py`（ファイル読み書き）
- `tests/`（テストコード）
- 機能そのもの（重複削除・並び替え・集計・複数統合）

---

## 完成後のウィンドウ構成

```
CTk（メインウィンドウ）
└── CTkTabview
    ├── タブ1：単体ファイル処理
    │   └── SingleProcessFrame（gui_single.py）
    └── タブ2：複数ファイル統合
        └── MergeFrame（gui_merge.py）
```

---

## 注意点

- `CTkComboBox` のコールバック引数は `ttk.Combobox` と異なる（`choice` 引数が必要）
- `CTkCheckBox` の変数は `ctk.BooleanVar` ではなく `tk.BooleanVar` を引き続き使用可能
- `CTkScrollableFrame` はフレームとして扱い、子ウィジェットを `pack` で積む
- `CTkScrollableFrame` 内のファイル一覧は `CTkLabel` を並べ、クリックで選択状態（背景色変更）を管理する。削除は選択中のインデックスを `file_paths` リストから `pop` する既存ロジックを流用する
