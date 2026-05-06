# ドラッグ＆ドロップ＋ウィンドウリサイズ 設計書

## 概要

2つの機能を追加する：
1. ファイルのドラッグ＆ドロップ読み込み（指定エリアのみ）
2. ウィンドウの任意サイズ変更

---

## 機能 1: ドラッグ＆ドロップ

### ドロップゾーン

| タブ | ドロップゾーン | 動作 |
|---|---|---|
| 単体ファイル処理 | ファイル選択エリア（`file_frame`） | Excel/CSV を1ファイル読み込み |
| 複数ファイル統合 | ファイル一覧エリア（`scroll_frame`） | Excel/CSV を複数追加 |

### 視覚フィードバック
- ドラッグ中（ファイルがエリア上にある間）：枠がブルーに変わる
- ドロップ後：通常の枠色に戻る
- 単体タブでは最初にドロップしたファイル1つのみ処理（複数ドロップされても先頭1つ）
- 統合タブでは複数ファイルをまとめてドロップ可能

### 対応ファイル形式
- `.xlsx`、`.csv` のみ受け付ける
- それ以外の拡張子はドロップしても無視する（エラーメッセージなし）

### 使用ライブラリ
- `tkinterdnd2`：requirements.txt に追加
- PyInstaller でのビルド時に `--collect-data tkinterdnd2` で同梱

---

## 機能 2: ウィンドウリサイズ

### 変更内容
- `main.py` の `root.resizable(False, False)` → `root.resizable(True, True)` に変更
- 最小ウィンドウサイズを設定：`root.minsize(500, 400)`（縮めすぎ防止）
- タブビュー・各フレームに `fill='both', expand=True` を追加してレイアウトが追従するよう調整

---

## 変更するファイル

| ファイル | 変更内容 |
|---|---|
| `requirements.txt` | `tkinterdnd2` を追加 |
| `main.py` | `TkinterDnD.Tk` に変更、resizable・minsize 設定、tabview レイアウト調整 |
| `gui_single.py` | `file_frame` にドロップゾーン設定・視覚フィードバック追加 |
| `gui_merge.py` | `scroll_frame` にドロップゾーン設定・視覚フィードバック追加 |

---

## .exe ビルド

```
pyinstaller --noconfirm --onefile --windowed \
  --collect-data customtkinter \
  --collect-data tkinterdnd2 \
  --name "データ整理ツール" main.py
```

---

## 注意点

- `tkinterdnd2` は `ctk.CTk()` ではなく `TkinterDnD.Tk()` をルートウィンドウとして使う必要がある
- CustomTkinter との組み合わせ: `root = TkinterDnD.Tk()` でウィンドウ作成後、`ctk.set_appearance_mode()` を適用する形にする（CTk() は使わない）
- ドロップイベントは `widget.drop_target_register(DND_FILES)` + `widget.dnd_bind('<<Drop>>', handler)` で登録する
