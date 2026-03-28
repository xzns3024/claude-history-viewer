import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from data import load_debug_files, fmt_size, CLAUDE_DIR
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM


class DebugTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.files = load_debug_files()
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG, pady=10)
        top.pack(fill='x', padx=16)
        self.count_label = tk.Label(top, bg=BG, fg=SUB, font=FONT_SM,
                                    text=f'共 {len(self.files)} 个调试文件')
        self.count_label.pack(side='left')
        tk.Button(top, text='删除所选', font=FONT_SM, bg='#C42B1C', fg='white',
                  relief='flat', padx=12, pady=3, cursor='hand2',
                  command=self._delete_selected).pack(side='right')
        tk.Button(top, text='全部删除', font=FONT_SM, bg='#8B0000', fg='white',
                  relief='flat', padx=12, pady=3, cursor='hand2',
                  command=self._delete_all).pack(side='right', padx=(0, 8))

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG, sashwidth=4, bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        cols = ('文件名', '大小', '时间')
        self.tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='extended')
        self.tree.heading('文件名', text='文件名')
        self.tree.heading('大小', text='大小')
        self.tree.heading('时间', text='修改时间')
        self.tree.column('文件名', width=240)
        self.tree.column('大小', width=70, anchor='e')
        self.tree.column('时间', width=150)
        sb = ttk.Scrollbar(left, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        pane.add(left, minsize=380)

        for fi in self.files:
            t = datetime.fromtimestamp(fi['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            self.tree.insert('', 'end', values=(fi['name'], fmt_size(fi['size']), t),
                             tags=(fi['path'],))

        right = tk.Frame(pane, bg=CARD)
        self.detail = tk.Text(right, bg=CARD, fg=TEXT, font=('Consolas', 9), relief='flat',
                              wrap='none', state='disabled', padx=12, pady=10)
        sb_y = ttk.Scrollbar(right, orient='vertical', command=self.detail.yview)
        sb_x = ttk.Scrollbar(right, orient='horizontal', command=self.detail.xview)
        self.detail.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.detail.pack(side='left', fill='both', expand=True)
        sb_y.pack(side='right', fill='y')
        pane.add(right, minsize=300)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        if not tags:
            return
        path = tags[0]
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                self.detail.insert('end', f.read())
        except Exception as e:
            self.detail.insert('end', f'读取失败: {e}')
        self.detail.config(state='disabled')

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno('确认删除', f'删除选中的 {len(sel)} 个文件？'):
            return
        for item in sel:
            tags = self.tree.item(item, 'tags')
            if tags:
                try:
                    os.remove(tags[0])
                except Exception:
                    pass
            self.tree.delete(item)
        self.files = load_debug_files()
        self.count_label.config(text=f'共 {len(self.files)} 个调试文件')

    def _delete_all(self):
        if not messagebox.askyesno('确认', '删除全部调试文件？'):
            return
        debug_dir = os.path.join(CLAUDE_DIR, 'debug')
        for fi in self.files:
            try:
                os.remove(fi['path'])
            except Exception:
                pass
        self.tree.delete(*self.tree.get_children())
        self.files = []
        self.count_label.config(text='共 0 个调试文件')
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.config(state='disabled')
