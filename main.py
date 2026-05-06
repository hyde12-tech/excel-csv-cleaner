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
