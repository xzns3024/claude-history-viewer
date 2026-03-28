import tkinter as tk
from tkinter import ttk
from data import load_usage_stats as load_sessions
from ui import (BG, CARD, TEXT, TEXT2, SUB, ACCENT, SUCCESS, WARN, DANGER,
                BORDER, FONT, FONT_SM, FONT_BOLD, make_separator)


class SessionsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.sessions = load_sessions()
        self._build()

    def _build(self):
        toolbar = tk.Frame(self, bg=BG, pady=14)
        toolbar.pack(fill='x', padx=20)

        search_wrap = tk.Frame(toolbar, bg=BORDER, padx=1, pady=1)
        search_wrap.pack(side='left')
        search_inner = tk.Frame(search_wrap, bg=CARD)
        search_inner.pack()
        tk.Label(search_inner, text='🔍', bg=CARD, fg=SUB,
                 font=('Segoe UI', 10)).pack(side='left', padx=(8, 2))
        self.search_var = tk.StringVar()
        tk.Entry(search_inner, textvariable=self.search_var, width=28,
                 bg=CARD, fg=TEXT, insertbackground=ACCENT,
                 relief='flat', font=FONT,
                 highlightthickness=0).pack(side='left', ipady=6, padx=(0, 8))
        self.search_var.trace('w', lambda *_: self._filter())

        self.count_label = tk.Label(toolbar, bg=BG, fg=SUB, font=FONT_SM)
        self.count_label.pack(side='right')

        make_separator(self).pack(fill='x')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG,
                              sashwidth=5, sashrelief='flat', bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        self._build_tree(left)
        pane.add(left, minsize=440)

        right = tk.Frame(pane, bg=CARD)
        self._build_detail(right)
        pane.add(right, minsize=300)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self._filter()

    def _build_tree(self, parent):
        cols = ('开始时间', '项目路径', '时长', '消息数', '输入Token', '输出Token')
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(frame, columns=cols,
                                  show='headings', selectmode='browse')
        widths = (145, 220, 60, 70, 90, 90)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor='w', stretch=(w == 220))

        sb = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        odd_bg = '#F7F8FA' if BG == '#F0F2F5' else '#2A2B2F'
        self.tree.tag_configure('odd',  background=odd_bg)
        self.tree.tag_configure('even', background=CARD)

    def _build_detail(self, parent):
        header = tk.Frame(parent, bg=CARD, pady=10, padx=16)
        header.pack(fill='x')
        tk.Label(header, text='会话详情', bg=CARD, fg=TEXT,
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

        self.detail.tag_configure('key', foreground=SUB,  font=FONT_SM)
        self.detail.tag_configure('val', foreground=TEXT,  font=FONT)
        self.detail.tag_configure('sep', foreground=BORDER)
        self.detail.tag_configure('good', foreground=SUCCESS, font=FONT_SM)
        self.detail.tag_configure('warn', foreground=WARN,    font=FONT_SM)

    def _filter(self):
        kw = self.search_var.get().lower()
        data = [
            s for s in self.sessions
            if not kw
            or kw in s.get('project_path', '').lower()
            or kw in s.get('session_id', '').lower()
        ]
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(data):
            t = s.get('start_time', '')[:19].replace('T', ' ')
            p = s.get('project_path', '')
            dur = f"{s.get('duration_minutes', 0)}m"
            msgs = s.get('user_message_count', 0) + s.get('assistant_message_count', 0)
            ito = f"{s.get('input_tokens', 0):,}"
            oto = f"{s.get('output_tokens', 0):,}"
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end',
                             values=(t, p, dur, msgs, ito, oto),
                             tags=(tag,), iid=str(i))
        self._sessions_filtered = data
        self.count_label.config(text=f'共 {len(data)} 个会话')

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        s = self._sessions_filtered[idx]

        tool_str = ', '.join(f"{k}({v})"
                             for k, v in s.get('tool_uses', {}).items())
        lang_str = ', '.join(f"{k}({v})"
                             for k, v in s.get('languages', {}).items())

        fields = [
            ('Session ID',  s.get('session_id', '')),
            ('项目路径',    s.get('project_path', '')),
            ('开始时间',    s.get('start_time', '')[:19].replace('T', ' ')),
            ('时长',        f"{s.get('duration_minutes', 0)} 分钟"),
            ('用户消息',    str(s.get('user_message_count', 0))),
            ('助手消息',    str(s.get('assistant_message_count', 0))),
            ('输入 Token',  f"{s.get('input_tokens', 0):,}"),
            ('输出 Token',  f"{s.get('output_tokens', 0):,}"),
            ('工具调用',    tool_str or '无'),
            ('语言',        lang_str or '无'),
            ('新增行',      str(s.get('lines_added', 0))),
            ('删除行',      str(s.get('lines_removed', 0))),
            ('修改文件',    str(s.get('files_modified', 0))),
            ('Git 提交',    str(s.get('git_commits', 0))),
            ('Git 推送',    str(s.get('git_pushes', 0))),
        ]

        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        for k, v in fields:
            self.detail.insert('end', f'{k}\n', 'key')
            self.detail.insert('end', f'{v}\n\n', 'val')
        self.detail.config(state='disabled')
