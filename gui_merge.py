import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from file_io import read_table, write_table
from processor import merge_files


class MergeFrame:
    def __init__(self, parent):
        self.parent = parent
        self.file_paths = []
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self.parent, text='統合するファイル（2つ以上）', anchor='w').pack(
            fill='x', padx=10, pady=(10, 0))

        self.scroll_frame = ctk.CTkScrollableFrame(self.parent, height=150)
        self.scroll_frame.pack(fill='x', padx=10, pady=(4, 8))

        from tkinterdnd2 import DND_FILES
        self.scroll_frame.drop_target_register(DND_FILES)
        self.scroll_frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.scroll_frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        self.scroll_frame.dnd_bind('<<Drop>>', self._on_drop)
        for child in self.scroll_frame.winfo_children():
            if child.winfo_class() == 'Canvas':
                child.drop_target_register(DND_FILES)
                child.dnd_bind('<<DragEnter>>', self._on_drag_enter)
                child.dnd_bind('<<DragLeave>>', self._on_drag_leave)
                child.dnd_bind('<<Drop>>', self._on_drop)
                break

        btn_frame = ctk.CTkFrame(self.parent, fg_color='transparent')
        btn_frame.pack(fill='x', padx=10, pady=(0, 8))
        ctk.CTkButton(
            btn_frame, text='ファイルを追加',
            command=self._add_files, width=130).pack(side='left')

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

    def _rebuild_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        for i, path in enumerate(self.file_paths):
            name = path.replace('\\', '/').split('/')[-1]
            row = ctk.CTkFrame(self.scroll_frame, fg_color='transparent')
            row.pack(fill='x', padx=2, pady=1)
            ctk.CTkLabel(row, text=name, anchor='w').pack(
                side='left', fill='x', expand=True, padx=4)
            ctk.CTkButton(
                row, text='×', width=28,
                fg_color='gray40', hover_color='gray30',
                command=lambda idx=i: self._remove_at(idx)).pack(side='right', padx=2)

    def _remove_at(self, index):
        self.file_paths.pop(index)
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
