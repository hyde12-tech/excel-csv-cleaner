import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from file_io import read_table, write_table
from processor import dedupe, sort_data, aggregate


class SingleProcessWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('単体ファイル処理')
        self.root.resizable(False, False)
        self.file_path = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        pad = {'padx': 10, 'pady': 5}

        # ファイル選択
        file_frame = ttk.LabelFrame(self.root, text='ファイル選択')
        file_frame.pack(fill='x', **pad)
        ttk.Entry(file_frame, textvariable=self.file_path, width=45, state='readonly').pack(side='left', padx=5, pady=5)
        ttk.Button(file_frame, text='ファイルを選択', command=self._select_file).pack(side='left', padx=5)

        # 処理オプション
        opt = ttk.LabelFrame(self.root, text='処理を選択')
        opt.pack(fill='x', **pad)

        # 重複削除
        self.do_dedupe = tk.BooleanVar()
        ttk.Checkbutton(opt, text='重複データを削除', variable=self.do_dedupe).grid(
            row=0, column=0, sticky='w', padx=5, pady=4)

        # 並び替え
        self.do_sort = tk.BooleanVar()
        ttk.Checkbutton(opt, text='並び替え', variable=self.do_sort).grid(
            row=1, column=0, sticky='w', padx=5, pady=4)
        ttk.Label(opt, text='列:').grid(row=1, column=1, padx=4)
        self.sort_col = tk.StringVar()
        self.sort_col_cb = ttk.Combobox(opt, textvariable=self.sort_col, width=14, state='readonly')
        self.sort_col_cb.grid(row=1, column=2, padx=4)
        self.sort_order = tk.StringVar(value='昇順')
        ttk.Radiobutton(opt, text='昇順', variable=self.sort_order, value='昇順').grid(row=1, column=3, padx=2)
        ttk.Radiobutton(opt, text='降順', variable=self.sort_order, value='降順').grid(row=1, column=4, padx=2)

        # 集計
        self.do_agg = tk.BooleanVar()
        ttk.Checkbutton(opt, text='集計', variable=self.do_agg).grid(
            row=2, column=0, sticky='w', padx=5, pady=4)
        ttk.Label(opt, text='グループ:').grid(row=2, column=1, padx=4)
        self.agg_group = tk.StringVar()
        self.agg_group_cb = ttk.Combobox(opt, textvariable=self.agg_group, width=12, state='readonly')
        self.agg_group_cb.grid(row=2, column=2, padx=4)
        ttk.Label(opt, text='集計列:').grid(row=2, column=3, padx=4)
        self.agg_value = tk.StringVar()
        self.agg_value_cb = ttk.Combobox(opt, textvariable=self.agg_value, width=12, state='readonly')
        self.agg_value_cb.grid(row=2, column=4, padx=4)

        ttk.Label(opt, text='集計方法:').grid(row=3, column=1, padx=4, pady=(0, 6))
        self.agg_method = tk.StringVar(value='合計')
        ttk.Combobox(opt, textvariable=self.agg_method, values=['合計', '平均', '件数'],
                     width=8, state='readonly').grid(row=3, column=2, padx=4)

        # 実行ボタン
        ttk.Button(self.root, text='実行する', command=self._run, width=22).pack(pady=15)

    def _select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[('Excel/CSV', '*.xlsx *.csv'), ('Excel', '*.xlsx'), ('CSV', '*.csv')]
        )
        if not path:
            return
        self.file_path.set(path)
        try:
            df = read_table(path)
            cols = list(df.columns)
            self.sort_col_cb['values'] = cols
            self.agg_group_cb['values'] = cols
            self.agg_value_cb['values'] = cols
            if cols:
                self.sort_col.set(cols[0])
                self.agg_group.set(cols[0])
                self.agg_value.set(cols[-1])
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
                col = self.sort_col.get()
                if col:
                    asc = self.sort_order.get() == '昇順'
                    df = sort_data(df, columns=[col], ascending=[asc])

            if self.do_agg.get():
                group = self.agg_group.get()
                value = self.agg_value.get()
                method_map = {'合計': 'sum', '平均': 'mean', '件数': 'count'}
                if group and value:
                    df = aggregate(df, group_by=group, value_col=value,
                                   method=method_map[self.agg_method.get()])

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
