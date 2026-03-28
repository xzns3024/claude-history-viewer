import json
import tkinter as tk
from tkinter import ttk, messagebox
from data import load_history, format_time, HISTORY_FILE
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM


class HistoryTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.all_records = load_history()
        self.filtered = self.all_records[:]
        self._build()

    def _build(self):
        # 工具栏
        top = tk.Frame(self, bg=BG, pady=10)
        top.pack(fill='x', padx=16)
        tk.Label(top, text='搜索', bg=BG, fg=SUB, font=FONT_SM).pack(side='left')
        self.search_var = tk.StringVar()
        tk.Entry(top, textvariable=self.search_var, width=28, bg=CARD, fg=TEXT,
                 insertbackground=ACCENT, relief='solid', bd=1,
                 font=FONT).pack(side='left', padx=(6, 20), ipady=4)
        tk.Label(top, text='项目', bg=BG, fg=SUB, font=FONT_SM).pack(side='left')
        projects = ['全部'] + sorted(set(r.get('project', '') for r in self.all_records))
        self.proj_var = tk.StringVar(value='全部')
        cb = ttk.Combobox(top, textvariable=self.proj_var, values=projects,
                          width=22, state='readonly', font=FONT_SM)
        cb.pack(side='left', padx=(6, 0), ipady=3)
        cb.bind('<<ComboboxSelected>>', lambda _: self._filter())
        self.search_var.trace('w', lambda *_: self._filter())

        bar = tk.Frame(self, bg=BG, pady=4)
        bar.pack(fill='x', padx=16)
        self.count_label = tk.Label(bar, bg=BG, fg=SUB, font=FONT_SM)
        self.count_label.pack(side='left')
        tk.Button(bar, text='删除所选', font=FONT_SM, bg='#C42B1C', fg='white',
                  activebackground='#A52515', activeforeground='white',
                  relief='flat', padx=12, pady=3,
                  cursor='hand2', command=self._delete_selected).pack(side='right')

        tk.Frame(self, bg='#E0E0E0', height=1).pack(fill='x')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG, sashwidth=4,
                               sashrelief='flat', bd=0)
        pane.pack(fill='both', expand=True, padx=0, pady=0)

        left = tk.Frame(pane, bg=BG)
        cols = ('时间', '项目', '内容')
        self.tree = ttk.Treeview(left, columns=cols, show='headings', selectmode='extended')
        for col, w in zip(cols, (155, 210, 360)):
            self.tree.heading(col, text=col if col != '内容' else '内容摘要')
            self.tree.column(col, width=w, anchor='w')
        sb = ttk.Scrollbar(left, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        pane.add(left, minsize=400)

        right = tk.Frame(pane, bg=CARD)
        self.detail = tk.Text(right, bg=CARD, fg=TEXT, font=FONT, relief='flat',
                              wrap='word', state='disabled', padx=12, pady=10,
                              selectbackground=ACCENT, selectforeground='#FFFFFF')
        dsb = ttk.Scrollbar(right, orient='vertical', command=self.detail.yview)
        self.detail.configure(yscrollcommand=dsb.set)
        self.detail.pack(side='left', fill='both', expand=True)
        dsb.pack(side='right', fill='y')
        pane.add(right, minsize=300)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self._filter()

    def _filter(self):
        kw = self.search_var.get().lower()
        proj = self.proj_var.get()
        self.filtered = [
            r for r in self.all_records
            if (proj == '全部' or r.get('project', '') == proj)
            and (not kw or kw in r.get('display', '').lower()
                 or kw in r.get('project', '').lower())
        ]
        self.tree.delete(*self.tree.get_children())
        for r in self.filtered:
            t = format_time(r['timestamp']) if r.get('timestamp') else ''
            p = r.get('project', '')
            d = r.get('display', '').replace('\n', ' ')[:80]
            self.tree.insert('', 'end', values=(t, p, d), tags=(json.dumps(r),))
        self.count_label.config(text=f'共 {len(self.filtered)} 条')

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        if not tags:
            return
        r = json.loads(tags[0])
        t = format_time(r['timestamp']) if r.get('timestamp') else ''
        content = (f"时间：{t}\n"
                   f"项目：{r.get('project', '')}\n"
                   f"Session ID：{r.get('sessionId', '')}\n"
                   f"\n{r.get('display', '')}")
        self.detail.config(state='normal')
        self.detail.delete('1.0', 'end')
        self.detail.insert('end', content)
        self.detail.config(state='disabled')

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno('确认删除', f'确定删除选中的 {len(sel)} 条记录？此操作不可撤销。'):
            return
        to_del = set()
        for item in sel:
            tags = self.tree.item(item, 'tags')
            if tags:
                r = json.loads(tags[0])
                to_del.add((r.get('timestamp'), r.get('sessionId')))
        self.all_records = [r for r in self.all_records
                            if (r.get('timestamp'), r.get('sessionId')) not in to_del]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            for r in self.all_records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        self._filter()
