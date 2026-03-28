import json
import tkinter as tk
from tkinter import ttk, messagebox
from data import load_history, format_time, HISTORY_FILE
from ui import (BG, CARD, TEXT, TEXT2, SUB, ACCENT, BORDER,
                FONT, FONT_SM, FONT_BOLD, FONT_H2,
                make_btn, make_danger_btn, make_separator)


class HistoryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.all_records = load_history()
        self.filtered = self.all_records[:]
        self._build()

    def _build(self):
        # ── 工具栏 ──────────────────────────────
        toolbar = tk.Frame(self, bg=BG, pady=14)
        toolbar.pack(fill='x', padx=20)

        # 搜索框
        search_wrap = tk.Frame(toolbar, bg=BORDER, padx=1, pady=1)
        search_wrap.pack(side='left')
        search_inner = tk.Frame(search_wrap, bg=CARD)
        search_inner.pack()
        tk.Label(search_inner, text='🔍', bg=CARD, fg=SUB,
                 font=('Segoe UI', 10)).pack(side='left', padx=(8, 2))
        self.search_var = tk.StringVar()
        tk.Entry(search_inner, textvariable=self.search_var, width=24,
                 bg=CARD, fg=TEXT, insertbackground=ACCENT,
                 relief='flat', font=FONT,
                 highlightthickness=0).pack(side='left', ipady=6, padx=(0, 8))
        self.search_var.trace('w', lambda *_: self._filter())

        # 项目筛选
        tk.Label(toolbar, text='项目', bg=BG, fg=SUB,
                 font=FONT_SM).pack(side='left', padx=(16, 4))
        projects = ['全部'] + sorted(set(r.get('project', '') for r in self.all_records))
        self.proj_var = tk.StringVar(value='全部')
        cb = ttk.Combobox(toolbar, textvariable=self.proj_var,
                          values=projects, width=20,
                          state='readonly', font=FONT_SM)
        cb.pack(side='left', ipady=4)
        cb.bind('<<ComboboxSelected>>', lambda _: self._filter())

        # 右侧按钮组
        make_danger_btn(self, '').pack_forget()  # 预热
        self.del_btn = make_danger_btn(toolbar, '删除所选',
                                       padx=14, pady=5)
        self.del_btn.config(command=self._delete_selected)
        self.del_btn.pack(side='right')

        self.count_label = tk.Label(toolbar, bg=BG, fg=SUB, font=FONT_SM)
        self.count_label.pack(side='right', padx=12)

        make_separator(self).pack(fill='x')

        # ── 主体分栏 ────────────────────────────
        pane = tk.PanedWindow(self, orient='horizontal', bg=BG,
                              sashwidth=5, sashrelief='flat',
                              sashpad=0, bd=0)
        pane.pack(fill='both', expand=True)

        # 左侧列表
        left = tk.Frame(pane, bg=BG)
        self._build_tree(left)
        pane.add(left, minsize=420)

        # 右侧详情
        right = tk.Frame(pane, bg=CARD)
        self._build_detail(right)
        pane.add(right, minsize=320)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self._filter()

    def _build_tree(self, parent):
        header = tk.Frame(parent, bg=CARD, pady=0)
        header.pack(fill='x')

        cols = ('时间', '项目', '内容摘要')
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(frame, columns=cols,
                                  show='headings', selectmode='extended')
        for col, w, anchor in zip(cols, (160, 190, 0), ('w', 'w', 'w')):
            self.tree.heading(col, text=col)
            if w:
                self.tree.column(col, width=w, anchor=anchor, stretch=False)
            else:
                self.tree.column(col, anchor=anchor, stretch=True)

        sb = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        # 斑马纹
        odd_bg = '#F7F8FA' if BG == '#F0F2F5' else '#2A2B2F'
        self.tree.tag_configure('odd', background=odd_bg)
        self.tree.tag_configure('even', background=CARD)

    def _build_detail(self, parent):
        header = tk.Frame(parent, bg=CARD, pady=10, padx=16)
        header.pack(fill='x')
        tk.Label(header, text='详情', bg=CARD, fg=TEXT,
                 font=FONT_BOLD).pack(side='left')
        make_separator(parent, bg=BORDER).pack(fill='x')

        self.detail = tk.Text(parent, bg=CARD, fg=TEXT, font=FONT,
                              relief='flat', wrap='word',
                              state='disabled', padx=16, pady=12,
                              selectbackground=ACCENT,
                              selectforeground='#FFFFFF',
                              spacing1=2, spacing3=2)
        dsb = ttk.Scrollbar(parent, orient='vertical',
                            command=self.detail.yview)
        self.detail.configure(yscrollcommand=dsb.set)
        self.detail.pack(side='left', fill='both', expand=True)
        dsb.pack(side='right', fill='y')

        self.detail.tag_configure('key',   foreground=SUB,   font=FONT_SM)
        self.detail.tag_configure('val',   foreground=TEXT,  font=FONT)
        self.detail.tag_configure('body',  foreground=TEXT2, font=FONT,
                                  lmargin1=4, lmargin2=4)
        self.detail.tag_configure('sep',   foreground=BORDER)

    def _filter(self):
        kw = self.search_var.get().lower()
        proj = self.proj_var.get()
        self.filtered = [
            r for r in self.all_records
            if (proj == '全部' or r.get('project', '') == proj)
            and (not kw
                 or kw in r.get('display', '').lower()
                 or kw in r.get('project', '').lower())
        ]
        self.tree.delete(*self.tree.get_children())
        for i, r in enumerate(self.filtered):
            t = format_time(r['timestamp']) if r.get('timestamp') else ''
            p = r.get('project', '')
            d = r.get('display', '').replace('\n', ' ')[:90]
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end', values=(t, p, d),
                             tags=(tag, json.dumps(r)))
        self.count_label.config(text=f'共 {len(self.filtered)} 条记录')

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        # tags[0]=斑马tag, tags[1]=json
        raw = next((t for t in tags if t.startswith('{')), None)
        if not raw:
            return
        r = json.loads(raw)
        t = format_time(r['timestamp']) if r.get('timestamp') else ''
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        for k, v in [('时间', t), ('项目', r.get('project', '')),
                     ('Session ID', r.get('sessionId', ''))]:
            self.detail.insert('end', f'{k}  ', 'key')
            self.detail.insert('end', f'{v}\n', 'val')
        self.detail.insert('end', '─' * 40 + '\n', 'sep')
        self.detail.insert('end', r.get('display', ''), 'body')
        self.detail.config(state='disabled')

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno('确认删除',
                                   f'确定删除选中的 {len(sel)} 条记录？此操作不可撤销。'):
            return
        to_del = set()
        for item in sel:
            tags = self.tree.item(item, 'tags')
            raw = next((t for t in tags if t.startswith('{')), None)
            if raw:
                r = json.loads(raw)
                to_del.add((r.get('timestamp'), r.get('sessionId')))
        self.all_records = [
            r for r in self.all_records
            if (r.get('timestamp'), r.get('sessionId')) not in to_del
        ]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            for r in self.all_records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        self._filter()
