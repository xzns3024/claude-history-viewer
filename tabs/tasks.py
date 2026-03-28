import tkinter as tk
from tkinter import ttk
from data import load_tasks
from ui import (BG, CARD, TEXT, TEXT2, SUB, ACCENT, SUCCESS, WARN, DANGER,
                BORDER, FONT, FONT_SM, FONT_BOLD, make_separator)

STATUS_META = {
    'completed':   ('已完成', SUCCESS,  '●'),
    'in_progress': ('进行中', ACCENT,   '◑'),
    'pending':     ('待处理', WARN,     '○'),
    'failed':      ('失败',   DANGER,   '✕'),
}


class TasksTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.tasks = load_tasks()
        self._build()

    def _build(self):
        toolbar = tk.Frame(self, bg=BG, pady=14)
        toolbar.pack(fill='x', padx=20)

        # 统计标签
        counts = {}
        for t in self.tasks:
            s = t.get('status', 'pending')
            counts[s] = counts.get(s, 0) + 1
        for status, (label, color, icon) in STATUS_META.items():
            cnt = counts.get(status, 0)
            chip = tk.Frame(toolbar, bg=CARD, padx=10, pady=4)
            chip.pack(side='left', padx=(0, 8))
            tk.Label(chip, text=f'{icon} {label} {cnt}',
                     bg=CARD, fg=color, font=FONT_SM).pack()

        self.count_label = tk.Label(toolbar, bg=BG, fg=SUB, font=FONT_SM,
                                    text=f'共 {len(self.tasks)} 个任务')
        self.count_label.pack(side='right')

        make_separator(self).pack(fill='x')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG,
                              sashwidth=5, sashrelief='flat', bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        self._build_tree(left)
        pane.add(left, minsize=420)

        right = tk.Frame(pane, bg=CARD)
        self._build_detail(right)
        pane.add(right, minsize=300)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self._load_tree()

    def _build_tree(self, parent):
        cols = ('状态', '标题', 'Session')
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(frame, columns=cols,
                                  show='headings', selectmode='browse')
        self.tree.heading('状态',   text='状态')
        self.tree.heading('标题',   text='标题')
        self.tree.heading('Session', text='Session ID')
        self.tree.column('状态',   width=80,  anchor='center', stretch=False)
        self.tree.column('标题',   width=240, anchor='w',      stretch=True)
        self.tree.column('Session', width=180, anchor='w',      stretch=False)

        sb = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        for status, (_, color, _) in STATUS_META.items():
            self.tree.tag_configure(status, foreground=color)
        odd_bg = '#F7F8FA' if BG == '#F0F2F5' else '#2A2B2F'
        self.tree.tag_configure('odd',  background=odd_bg)
        self.tree.tag_configure('even', background=CARD)

    def _build_detail(self, parent):
        header = tk.Frame(parent, bg=CARD, pady=10, padx=16)
        header.pack(fill='x')
        tk.Label(header, text='任务详情', bg=CARD, fg=TEXT,
                 font=FONT_BOLD).pack(side='left')
        make_separator(parent, bg=BORDER).pack(fill='x')

        self.detail = tk.Text(parent, bg=CARD, fg=TEXT, font=FONT,
                              relief='flat', wrap='word',
                              state='disabled', padx=16, pady=12,
                              selectbackground=ACCENT,
                              selectforeground='#FFFFFF',
                              spacing1=3, spacing3=3)
        dsb = ttk.Scrollbar(parent, orient='vertical',
                            command=self.detail.yview)
        self.detail.configure(yscrollcommand=dsb.set)
        self.detail.pack(side='left', fill='both', expand=True)
        dsb.pack(side='right', fill='y')

        self.detail.tag_configure('key',     foreground=SUB,     font=FONT_SM)
        self.detail.tag_configure('val',     foreground=TEXT,    font=FONT)
        self.detail.tag_configure('status',  foreground=ACCENT,  font=FONT_BOLD)
        self.detail.tag_configure('content', foreground=TEXT2,   font=FONT,
                                  lmargin1=4, lmargin2=4)

    def _load_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, t in enumerate(self.tasks):
            status = t.get('status', 'pending')
            meta   = STATUS_META.get(status, ('?', SUB, '?'))
            icon   = meta[2]
            sid    = t.get('_session_id', '')[:18] + '…'
            tag1   = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end',
                             values=(f'{icon} {meta[0]}',
                                     t.get('subject', ''),
                                     sid),
                             tags=(status, tag1),
                             iid=str(i))

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        t = self.tasks[int(sel[0])]
        status  = t.get('status', '')
        meta    = STATUS_META.get(status, (status, SUB, '?'))

        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.insert('end', f"{meta[2]} {meta[0]}\n\n", 'status')
        for k, v in [('标题',      t.get('subject', '')),
                     ('Session',   t.get('_session_id', '')),
                     ('状态',      status)]:
            self.detail.insert('end', f'{k}\n', 'key')
            self.detail.insert('end', f'{v}\n\n', 'val')
        if t.get('content'):
            self.detail.insert('end', '内容\n', 'key')
            self.detail.insert('end', str(t['content']), 'content')
        self.detail.config(state='disabled')
