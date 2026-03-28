import tkinter as tk
from tkinter import ttk
from data import load_tasks
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM

STATUS_COLOR = {
    'completed': '#107C10',
    'in_progress': '#0078D4',
    'pending': '#605E5C',
    'failed': '#C42B1C',
}


class TasksTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.tasks = load_tasks()
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG, pady=10)
        top.pack(fill='x', padx=16)
        tk.Label(top, text=f'共 {len(self.tasks)} 个任务', bg=BG, fg=SUB, font=FONT_SM).pack(side='left')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG, sashwidth=4, bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        cols = ('状态', '标题', 'Session')
        self.tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='browse')
        self.tree.heading('状态', text='状态')
        self.tree.heading('标题', text='标题')
        self.tree.heading('Session', text='Session ID')
        self.tree.column('状态', width=90)
        self.tree.column('标题', width=220)
        self.tree.column('Session', width=200)
        sb = ttk.Scrollbar(left, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        pane.add(left, minsize=400)

        for t in self.tasks:
            status = t.get('status', '')
            self.tree.insert('', 'end',
                             values=(status, t.get('subject', ''), t.get('_session_id', '')[:16] + '...'),
                             tags=(status, str(self.tasks.index(t))))

        # 状态颜色
        for s, c in STATUS_COLOR.items():
            self.tree.tag_configure(s, foreground=c)

        right = tk.Frame(pane, bg=CARD)
        self.detail = tk.Text(right, bg=CARD, fg=TEXT, font=FONT, relief='flat',
                              wrap='word', state='disabled', padx=12, pady=10)
        dsb = ttk.Scrollbar(right, orient='vertical', command=self.detail.yview)
        self.detail.configure(yscrollcommand=dsb.set)
        self.detail.pack(side='left', fill='both', expand=True)
        dsb.pack(side='right', fill='y')
        pane.add(right, minsize=300)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        if len(tags) < 2:
            return
        idx = int(tags[1])
        t = self.tasks[idx]
        content = (f"标题: {t.get('subject', '')}\n"
                   f"状态: {t.get('status', '')}\n"
                   f"Session ID: {t.get('_session_id', '')}\n"
                   f"当前阶段: {t.get('activeForm', '')}\n\n"
                   f"描述:\n{t.get('description', '')}\n\n"
                   f"阻塞: {', '.join(t.get('blocks', [])) or '无'}\n"
                   f"被阻塞: {', '.join(t.get('blockedBy', [])) or '无'}")
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.insert('end', content)
        self.detail.config(state='disabled')
