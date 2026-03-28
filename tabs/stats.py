import tkinter as tk
from tkinter import ttk
from data import load_usage_stats as load_stats
from ui import (BG, CARD, ACCENT, SUCCESS, WARN, DANGER, TEXT, TEXT2, SUB,
                BORDER, FONT, FONT_SM, FONT_BOLD, FONT_H1, FONT_H2,
                FONT_NUM, make_separator)

CARD_ACCENTS = [ACCENT, SUCCESS, WARN, '#722ED1', '#13C2C2', DANGER]


def _aggregate(sessions):
    s = {}
    s['total_sessions'] = len(sessions)
    s['total_input_tokens'] = sum(x.get('input_tokens', 0) for x in sessions)
    s['total_output_tokens'] = sum(x.get('output_tokens', 0) for x in sessions)
    s['total_duration_minutes'] = sum(x.get('duration_minutes', 0) for x in sessions)
    s['total_user_messages'] = sum(x.get('user_message_count', 0) for x in sessions)
    s['total_assistant_messages'] = sum(x.get('assistant_message_count', 0) for x in sessions)
    s['total_lines_added'] = sum(x.get('lines_added', 0) for x in sessions)
    s['total_lines_removed'] = sum(x.get('lines_removed', 0) for x in sessions)
    s['total_files_modified'] = sum(x.get('files_modified', 0) for x in sessions)
    s['total_git_commits'] = sum(x.get('git_commits', 0) for x in sessions)
    s['total_tool_errors'] = sum(x.get('tool_errors', 0) for x in sessions)
    # 汇总工具调用
    tool_counts = {}
    for x in sessions:
        for k, v in x.get('tool_counts', {}).items():
            tool_counts[k] = tool_counts.get(k, 0) + v
    s['tool_counts'] = tool_counts
    # 汇总语言
    lang_counts = {}
    for x in sessions:
        for k, v in x.get('languages', {}).items():
            lang_counts[k] = lang_counts.get(k, 0) + v
    s['lang_counts'] = lang_counts
    return s


class StatsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.stats = _aggregate(load_stats())
        self._build()

    def _build(self):
        # 标题栏
        header = tk.Frame(self, bg=BG, pady=16)
        header.pack(fill='x', padx=20)
        tk.Label(header, text='使用统计', bg=BG, fg=TEXT,
                 font=FONT_H1).pack(side='left')
        tk.Label(header, text='累计数据总览', bg=BG, fg=SUB,
                 font=FONT_SM).pack(side='left', padx=(12, 0), pady=2)

        make_separator(self).pack(fill='x', padx=20, pady=(0, 16))

        # 滚动容器
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor='nw')

        def _on_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind('<Configure>', _on_resize)
        inner.bind('<Configure>',
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox('all')))
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(
                            int(-1 * e.delta / 120), 'units'))

        self._render_cards(inner)
        self._render_breakdown(inner)

    def _render_cards(self, parent):
        s = self.stats
        total_tokens = s.get('total_input_tokens', 0) + s.get('total_output_tokens', 0)
        cards = [
            ('总会话数', s.get('total_sessions', 0), '次', ACCENT),
            ('用户消息数', s.get('total_user_messages', 0), '条', SUCCESS),
            ('总Token用量', f"{total_tokens:,}", '', WARN),
            ('总使用时长', f"{s.get('total_duration_minutes', 0):,}", '分钟', '#722ED1'),
            ('修改文件数', s.get('total_files_modified', 0), '个', '#13C2C2'),
            ('Git 提交数', s.get('total_git_commits', 0), '次', DANGER),
        ]

        row = tk.Frame(parent, bg=BG)
        row.pack(fill='x', padx=20, pady=(0, 8))
        for i, (label, val, unit, color) in enumerate(cards):
            card = tk.Frame(row, bg=CARD, padx=20, pady=18)
            card.grid(row=0, column=i, padx=6, pady=6, sticky='nsew')
            row.grid_columnconfigure(i, weight=1)

            # 顶部色条
            tk.Frame(card, bg=color, height=3).pack(fill='x', pady=(0, 10))

            val_str = str(val) if isinstance(val, str) else f'{val:,}'
            num_lbl = tk.Label(card, text=val_str, bg=CARD, fg=color,
                               font=FONT_NUM)
            num_lbl.pack()
            if unit:
                tk.Label(card, text=unit, bg=CARD, fg=TEXT2,
                         font=FONT_SM).pack()
            tk.Label(card, text=label, bg=CARD, fg=SUB,
                     font=FONT_SM).pack(pady=(6, 0))

    def _render_breakdown(self, parent):
        s = self.stats
        sections = [
            ('Token 分布', [
                ('输入 Token', s.get('total_input_tokens', 0), ACCENT),
                ('输出 Token', s.get('total_output_tokens', 0), SUCCESS),
            ]),
            ('代码变更', [
                ('新增行数', s.get('total_lines_added', 0), SUCCESS),
                ('删除行数', s.get('total_lines_removed', 0), DANGER),
                ('修改文件', s.get('total_files_modified', 0), WARN),
            ]),
            ('协作指标', [
                ('用户消息', s.get('total_user_messages', 0), ACCENT),
                ('助手消息', s.get('total_assistant_messages', 0), '#722ED1'),
                ('工具错误', s.get('total_tool_errors', 0), '#13C2C2'),
                ('Git 提交', s.get('total_git_commits', 0), WARN),
            ]),
        ]

        container = tk.Frame(parent, bg=BG)
        container.pack(fill='x', padx=20, pady=(8, 20))

        for col_idx, (title, items) in enumerate(sections):
            card = tk.Frame(container, bg=CARD, padx=20, pady=16)
            card.grid(row=0, column=col_idx, padx=6, sticky='nsew')
            container.grid_columnconfigure(col_idx, weight=1)

            tk.Label(card, text=title, bg=CARD, fg=TEXT,
                     font=FONT_BOLD).pack(anchor='w')
            tk.Frame(card, bg=BORDER, height=1).pack(fill='x', pady=(6, 12))

            total = sum(v for _, v, _ in items) or 1
            for label, val, color in items:
                row = tk.Frame(card, bg=CARD)
                row.pack(fill='x', pady=4)
                tk.Label(row, text=label, bg=CARD, fg=TEXT2,
                         font=FONT_SM, width=10, anchor='w').pack(side='left')
                pct = val / total
                bar_bg = tk.Frame(row, bg=BORDER, height=8)
                bar_bg.pack(side='left', fill='x', expand=True, padx=(8, 8))
                bar_bg.update_idletasks()

                def _draw_bar(bg=bar_bg, c=color, p=pct):
                    w = int(bg.winfo_width() * p)
                    if w > 0:
                        tk.Frame(bg, bg=c, height=8, width=w).place(x=0, y=0)
                bar_bg.bind('<Map>', lambda e, fn=_draw_bar: fn())

                val_str = f'{val:,}'
                tk.Label(row, text=val_str, bg=CARD, fg=color,
                         font=FONT_SM, width=10, anchor='e').pack(side='right')
