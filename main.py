import tkinter as tk
from tkinter import ttk
from gui_single import SingleProcessWindow
from gui_merge import MergeWindow


def main():
    root = tk.Tk()
    root.title('Excel/CSV データ整理ツール')
    root.resizable(False, False)

    ttk.Label(root, text='Excel/CSV データ整理ツール', font=('', 15, 'bold')).pack(pady=(25, 5))
    ttk.Label(root, text='処理モードを選んでください', foreground='gray').pack(pady=(0, 20))

    def open_single():
        win = tk.Toplevel(root)
        SingleProcessWindow(win)

    def open_merge():
        win = tk.Toplevel(root)
        MergeWindow(win)

    btn_frame = ttk.Frame(root)
    btn_frame.pack(padx=40, pady=5)

    ttk.Button(btn_frame, text='📄  単体ファイル処理\n    重複削除・並び替え・集計',
               command=open_single, width=28).pack(pady=6)
    ttk.Button(btn_frame, text='📑  複数ファイル統合\n    複数ファイルを1つにまとめる',
               command=open_merge, width=28).pack(pady=6)

    ttk.Label(root, text='').pack(pady=5)

    root.mainloop()


if __name__ == '__main__':
    main()
