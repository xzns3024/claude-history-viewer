import os
import tkinter as tk
from tkinter import ttk
from data import load_file_history, fmt_size
from ui import (BG, CARD, TEXT, TEXT2, SUB, ACCENT, BORDER,
                FONT, FONT_SM, FONT_BOLD, make_separator)


class FileHistoryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.data = load_file_history()
        self._build()

    def _build(self):
        toolbar = tk.Frame(self, bg=BG, pady=14)
        toolbar.pack(fill='x', padx=20)
        total = sum(len(s['versions']) for s in self.data)
        tk.Label(toolbar,
                 text=f'共 {len(self.data)} 个会话  ·  {total} 个版本文件',
                 bg=BG, fg=SUB, font=FONT_SM).pack(side='left')

        make_separator(self).pack(fill='x')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG,
                              sashwidth=5, sashrelief='flat', bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        self._build_tree(left)
        pane.add(left, minsize=360)

        right = tk.Frame(pane, bg=CARD)
        self._build_detail(right)
        pane.add(right, minsize=300)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _build_tree(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(frame, show='tree headings',
                                  columns=('大小',), selectmode='browse')
        self.tree.heading('#0',  text='会话 / 版本文件')
        self.tree.heading('大小', text='大小')
        self.tree.column('#0',  width=280, stretch=True)
        self.tree.column('大小', width=80,  anchor='e', stretch=False)

        sb = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        self.tree.tag_configure('session', foreground=ACCENT, font=FONT_BOLD)
        self.tree.tag_configure('version', foreground=TEXT2)

        for s in self.data:
            sid = s['session_id']
            label = sid[:20] + '…' if len(sid) > 20 else sid
            node = self.tree.insert('', 'end', text=f'📁 {label}',
                                    values=('',), open=False,
                                    tags=('session',))
            for v in s['versions']:
                self.tree.insert(node, 'end', text=f'  {v["name"]}',
                                 values=(fmt_size(v['size']),),
                                 tags=(v['path'], 'version'))

    def _build_detail(self, parent):
        header = tk.Frame(parent, bg=CARD, pady=10, padx=16)
        header.pack(fill='x')
        tk.Label(header, text='版本内容', bg=CARD, fg=TEXT,
                 font=FONT_BOLD).pack(side='left')
        make_separator(parent, bg=BORDER).pack(fill='x')

        self.detail = tk.Text(parent, bg=CARD, fg=TEXT2,
                              font=('Consolas', 9),
                              relief='flat', wrap='none',
                              state='disabled', padx=16, pady=12)
        sb_y = ttk.Scrollbar(parent, orient='vertical',
                             command=self.detail.yview)
        sb_x = ttk.Scrollbar(parent, orient='horizontal',
                             command=self.detail.xview)
        self.detail.configure(yscrollcommand=sb_y.set,
                              xscrollcommand=sb_x.set)
        self.detail.pack(side='left', fill='both', expand=True)
        sb_y.pack(side='right', fill='y')

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        path = next((t for t in tags
                     if t not in ('session', 'version')
                     and (os.sep in t or '/' in t)), None)
        if not path:
            return
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                self.detail.insert('end', f.read())
        except Exception as e:
            self.detail.insert('end', f'读取失败: {e}')
        self.detail.config(state='disabled')
