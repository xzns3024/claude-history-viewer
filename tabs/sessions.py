import tkinter as tk
from tkinter import ttk
from data import load_sessions, load_session_messages, fmt_size
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM
from datetime import datetime


class SessionsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.sessions = load_sessions()
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG, pady=10)
        top.pack(fill='x', padx=16)
        tk.Label(top, text=f'共 {len(self.sessions)} 个会话', bg=BG, fg=SUB, font=FONT_SM).pack(side='left')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG, sashwidth=4, bd=0)
        pane.pack(fill='both', expand=True)

        # 左侧会话列表
        left = tk.Frame(pane, bg=BG)
        cols = ('时间', '项目', '大小')
        self.tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='browse')
        self.tree.heading('时间', text='最后修改')
        self.tree.heading('项目', text='项目')
        self.tree.heading('大小', text='大小')
        self.tree.column('时间', width=150)
        self.tree.column('项目', width=180)
        self.tree.column('大小', width=70, anchor='e')
        sb = ttk.Scrollbar(left, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        pane.add(left, minsize=350)

        for s in self.sessions:
            t = datetime.fromtimestamp(s['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            self.tree.insert('', 'end', values=(t, s['project'], fmt_size(s['size'])),
                             tags=(s['path'],))

        # 右侧对话内容
        right = tk.Frame(pane, bg=CARD)
        self.detail = tk.Text(right, bg=CARD, fg=TEXT, font=FONT, relief='flat',
                              wrap='word', state='disabled', padx=12, pady=10)
        dsb = ttk.Scrollbar(right, orient='vertical', command=self.detail.yview)
        self.detail.configure(yscrollcommand=dsb.set)
        self.detail.pack(side='left', fill='both', expand=True)
        dsb.pack(side='right', fill='y')
        pane.add(right, minsize=400)

        self.detail.tag_configure('user', foreground='#0078D4', font=('Segoe UI', 10, 'bold'))
        self.detail.tag_configure('assistant', foreground='#107C10', font=('Segoe UI', 10, 'bold'))
        self.detail.tag_configure('body', foreground=TEXT, font=FONT)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        if not tags:
            return
        path = tags[0]
        messages = load_session_messages(path)
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        if not messages:
            self.detail.insert('end', '（无消息记录）')
        for msg in messages:
            role = msg.get('type', '')
            label = 'User' if role == 'user' else 'Assistant'
            tag = 'user' if role == 'user' else 'assistant'
            ts = msg.get('timestamp', '')
            if ts:
                try:
                    from datetime import timezone
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    ts = dt.strftime('%H:%M:%S')
                except Exception:
                    pass
            self.detail.insert('end', f'[{label}] {ts}\n', tag)
            content = msg.get('message', {})
            if isinstance(content, dict):
                parts = content.get('content', '')
                if isinstance(parts, str):
                    self.detail.insert('end', parts + '\n\n', 'body')
                elif isinstance(parts, list):
                    for p in parts:
                        if isinstance(p, dict) and p.get('type') == 'text':
                            self.detail.insert('end', p.get('text', '') + '\n\n', 'body')
        self.detail.config(state='disabled')
