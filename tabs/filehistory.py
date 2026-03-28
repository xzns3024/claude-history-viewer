import os
import tkinter as tk
from tkinter import ttk
from data import load_file_history, fmt_size
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM


class FileHistoryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.data = load_file_history()
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG, pady=10)
        top.pack(fill='x', padx=16)
        total = sum(len(s['versions']) for s in self.data)
        tk.Label(top, text=f'共 {len(self.data)} 个会话，{total} 个版本文件',
                 bg=BG, fg=SUB, font=FONT_SM).pack(side='left')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG, sashwidth=4, bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        self.tree = ttk.Treeview(left, show='tree headings',
                                  columns=('大小',), selectmode='browse')
        self.tree.heading('#0', text='会话 / 版本文件')
        self.tree.heading('大小', text='大小')
        self.tree.column('#0', width=280)
        self.tree.column('大小', width=80, anchor='e')
        sb = ttk.Scrollbar(left, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        pane.add(left, minsize=360)

        for s in self.data:
            sid = s['session_id']
            node = self.tree.insert('', 'end', text=sid[:16] + '...',
                                    values=('',), open=False)
            for v in s['versions']:
                self.tree.insert(node, 'end', text=v['name'],
                                 values=(fmt_size(v['size']),),
                                 tags=(v['path'],))

        right = tk.Frame(pane, bg=CARD)
        self.detail = tk.Text(right, bg=CARD, fg=TEXT, font=('Consolas', 9),
                              relief='flat', wrap='none', state='disabled',
                              padx=12, pady=10)
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
                content = f.read()
            self.detail.insert('end', content)
        except Exception as e:
            self.detail.insert('end', f'读取失败: {e}')
        self.detail.config(state='disabled')
