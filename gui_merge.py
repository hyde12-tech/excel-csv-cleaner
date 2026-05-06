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
