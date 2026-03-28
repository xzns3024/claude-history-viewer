import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from data import load_debug_files, fmt_size, CLAUDE_DIR
from ui import (BG, CARD, TEXT, TEXT2, SUB, ACCENT, DANGER, BORDER,
                FONT, FONT_SM, FONT_BOLD, make_separator,
                make_btn, make_danger_btn)


class DebugTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.files = load_debug_files()
        self._build()

    def _build(self):
        toolbar = tk.Frame(self, bg=BG, pady=14)
        toolbar.pack(fill='x', padx=20)

        self.count_label = tk.Label(toolbar, bg=BG, fg=SUB, font=FONT_SM,
                                    text=f'共 {len(self.files)} 个调试文件')
        self.count_label.pack(side='left')

        make_danger_btn(toolbar, '全部删除', padx=12, pady=5,
                        command=self._delete_all).pack(side='right', padx=(6, 0))
        make_danger_btn(toolbar, '删除所选', padx=12, pady=5,
                        command=self._delete_selected).pack(side='right')

        make_separator(self).pack(fill='x')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG,
                              sashwidth=5, sashrelief='flat', bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        self._build_tree(left)
        pane.add(left, minsize=380)

        right = tk.Frame(pane, bg=CARD)
        self._build_detail(right)
        pane.add(right, minsize=300)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _build_tree(self, parent):
        cols = ('文件名', '大小', '修改时间')
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(frame, columns=cols,
                                  show='headings', selectmode='extended')
        self.tree.heading('文件名',   text='文件名')
        self.tree.heading('大小',     text='大小')
        self.tree.heading('修改时间', text='修改时间')
        self.tree.column('文件名',   width=240, anchor='w', stretch=True)
        self.tree.column('大小',     width=80,  anchor='e', stretch=False)
        self.tree.column('修改时间', width=155, anchor='w', stretch=False)

        sb = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        odd_bg = '#F7F8FA' if BG == '#F0F2F5' else '#2A2B2F'
        self.tree.tag_configure('odd',  background=odd_bg)
        self.tree.tag_configure('even', background=CARD)

        for i, fi in enumerate(self.files):
            t = datetime.fromtimestamp(fi['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end',
                             values=(fi['name'], fmt_size(fi['size']), t),
                             tags=(tag, fi['path']))

    def _build_detail(self, parent):
        header = tk.Frame(parent, bg=CARD, pady=10, padx=16)
        header.pack(fill='x')
        tk.Label(header, text='文件内容', bg=CARD, fg=TEXT,
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
        # tags = (odd/even, path)
        path = next((t for t in tags if os.sep in t or '/' in t), None)
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

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno('确认删除',
                                   f'删除选中的 {len(sel)} 个文件？'):
            return
        for item in sel:
            tags = self.tree.item(item, 'tags')
            path = next((t for t in tags if os.sep in t or '/' in t), None)
            if path:
                try:
                    os.remove(path)
                except Exception:
                    pass
            self.tree.delete(item)
        self.files = load_debug_files()
        self.count_label.config(text=f'共 {len(self.files)} 个调试文件')

    def _delete_all(self):
        if not messagebox.askyesno('确认', '删除全部调试文件？'):
            return
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
