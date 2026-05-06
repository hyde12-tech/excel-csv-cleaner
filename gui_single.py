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
