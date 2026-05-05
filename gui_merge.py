import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from file_io import read_table, write_table
from processor import merge_files


class MergeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('複数ファイル統合')
        self.root.resizable(False, False)
        self.file_paths = []
        self._build_ui()

    def _build_ui(self):
        pad = {'padx': 10, 'pady': 5}

        list_frame = ttk.LabelFrame(self.root, text='統合するファイル（2つ以上）')
        list_frame.pack(fill='both', expand=True, **pad)

        self.listbox = tk.Listbox(list_frame, width=50, height=8, selectmode=tk.SINGLE)
        self.listbox.pack(side='left', padx=5, pady=5)

        sb = ttk.Scrollbar(list_frame, command=self.listbox.yview)
        sb.pack(side='left', fill='y', pady=5)
        self.listbox.configure(yscrollcommand=sb.set)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(side='left', padx=10)
        ttk.Button(btn_frame, text='ファイルを追加', command=self._add_files).pack(pady=4)
        ttk.Button(btn_frame, text='選択を削除', command=self._remove_selected).pack(pady=4)

        ttk.Button(self.root, text='統合する', command=self._run, width=22).pack(pady=15)

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            filetypes=[('Excel/CSV', '*.xlsx *.csv'), ('Excel', '*.xlsx'), ('CSV', '*.csv')]
        )
        for path in paths:
            if path not in self.file_paths:
                self.file_paths.append(path)
                name = path.replace('\\', '/').split('/')[-1]
                self.listbox.insert(tk.END, name)

    def _remove_selected(self):
        selected = self.listbox.curselection()
        if selected:
            idx = selected[0]
            self.listbox.delete(idx)
            self.file_paths.pop(idx)

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
