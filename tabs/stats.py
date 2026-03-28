import tkinter as tk
from tkinter import ttk
from data import load_usage_stats, fmt_size
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM


class StatsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.stats = load_usage_stats()
        self._build()

    def _build(self):
        # 汇总栏
        summary = tk.Frame(self, bg=CARD, pady=10)
        summary.pack(fill='x', padx=16, pady=(10, 0))
        total_in = sum(s.get('input_tokens', 0) for s in self.stats)
        total_out = sum(s.get('output_tokens', 0) for s in self.stats)
        total_min = sum(s.get('duration_minutes', 0) for s in self.stats)
        total_files = sum(s.get('files_modified', 0) for s in self.stats)
        total_lines = sum(s.get('lines_added', 0) for s in self.stats)
        items = [
            ('会话数', str(len(self.stats))),
            ('总时长', f'{total_min} 分钟'),
            ('输入 Token', f'{total_in:,}'),
            ('输出 Token', f'{total_out:,}'),
            ('修改文件', str(total_files)),
            ('新增行数', f'{total_lines:,}'),
        ]
        for i, (label, val) in enumerate(items):
            f = tk.Frame(summary, bg=CARD, padx=20)
            f.pack(side='left', expand=True)
            tk.Label(f, text=val, bg=CARD, fg=ACCENT, font=('Segoe UI', 14, 'bold')).pack()
            tk.Label(f, text=label, bg=CARD, fg=SUB, font=FONT_SM).pack()

        tk.Frame(self, bg='#E0E0E0', height=1).pack(fill='x', pady=8)

        # 明细表格
        cols = ('时间', '项目', '时长(分)', '输入Token', '输出Token', '工具调用', '文件', '行数')
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill='both', expand=True, padx=16, pady=(0, 10))
        self.tree = ttk.Treeview(frame, columns=cols, show='headings', selectmode='browse')
        widths = (150, 180, 70, 100, 100, 80, 60, 70)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor='e' if w <= 100 else 'w')
        sb_y = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        sb_x = ttk.Scrollbar(frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb_y.pack(side='right', fill='y')

        self._populate()
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        # 详情面板
        self.detail = tk.Text(self, bg=CARD, fg=TEXT, font=FONT_SM, relief='flat',
                              wrap='word', state='disabled', padx=12, pady=8, height=8)
        sb_d = ttk.Scrollbar(self, orient='vertical', command=self.detail.yview)
        self.detail.configure(yscrollcommand=sb_d.set)
        self.detail.pack(side='bottom', fill='x', padx=16, pady=(0, 10))

    def _populate(self):
        self.tree.delete(*self.tree.get_children())
        for s in self.stats:
            t = s.get('start_time', '')[:19].replace('T', ' ')
            proj = s.get('project_path', '').replace('\\', '/').split('/')[-1]
            dur = s.get('duration_minutes', 0)
            inp = s.get('input_tokens', 0)
            out = s.get('output_tokens', 0)
            tools = sum(s.get('tool_counts', {}).values())
            files = s.get('files_modified', 0)
            lines = s.get('lines_added', 0)
            self.tree.insert('', 'end', values=(t, proj, dur, f'{inp:,}', f'{out:,}', tools, files, lines),
                             tags=(s.get('session_id', ''),))

    def _sort(self, col):
        pass  # 简单实现，后续可扩展

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        if not tags:
            return
        sid = tags[0]
        s = next((x for x in self.stats if x.get('session_id') == sid), None)
        if not s:
            return
        tool_str = ', '.join(f'{k}:{v}' for k, v in s.get('tool_counts', {}).items())
        lang_str = ', '.join(f'{k}:{v}' for k, v in s.get('languages', {}).items())
        content = (f"Session ID: {s.get('session_id', '')}\n"
                   f"项目路径: {s.get('project_path', '')}\n"
                   f"开始时间: {s.get('start_time', '')[:19].replace('T', ' ')}\n"
                   f"时长: {s.get('duration_minutes', 0)} 分钟\n"
                   f"用户消息: {s.get('user_message_count', 0)}  助手消息: {s.get('assistant_message_count', 0)}\n"
                   f"输入Token: {s.get('input_tokens', 0):,}  输出Token: {s.get('output_tokens', 0):,}\n"
                   f"工具调用: {tool_str or '无'}\n"
                   f"语言: {lang_str or '无'}\n"
                   f"新增行: {s.get('lines_added', 0)}  删除行: {s.get('lines_removed', 0)}  修改文件: {s.get('files_modified', 0)}\n"
                   f"Git提交: {s.get('git_commits', 0)}  Git推送: {s.get('git_pushes', 0)}")
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.insert('end', content)
        self.detail.config(state='disabled')
