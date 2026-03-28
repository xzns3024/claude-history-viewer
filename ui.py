import tkinter as tk
from tkinter import ttk

BG = '#F3F3F3'
CARD = '#FFFFFF'
ACCENT = '#0078D4'
TEXT = '#1A1A1A'
SUB = '#605E5C'
BORDER = '#E0E0E0'
FONT = ('Segoe UI', 10)
FONT_SM = ('Segoe UI', 9)


def apply_style():
    s = ttk.Style()
    s.theme_use('clam')
    s.configure('Treeview', background=CARD, foreground=TEXT,
                fieldbackground=CARD, rowheight=28, font=FONT)
    s.configure('Treeview.Heading', background=BG, foreground=SUB,
                font=('Segoe UI', 9, 'bold'), relief='flat')
    s.map('Treeview', background=[('selected', ACCENT)],
          foreground=[('selected', '#FFFFFF')])
    s.configure('TCombobox', relief='flat')
    s.configure('Vertical.TScrollbar', troughcolor=BG, background=BORDER)


def build_toolbar(root, all_records, search_var, proj_var):
    top = tk.Frame(root, bg=BG, pady=10)
    top.pack(fill='x', padx=16)
    tk.Label(top, text='搜索', bg=BG, fg=SUB, font=FONT_SM).pack(side='left')
    tk.Entry(top, textvariable=search_var, width=28, bg=CARD, fg=TEXT,
             insertbackground=ACCENT, relief='solid', bd=1,
             font=FONT).pack(side='left', padx=(6, 20), ipady=4)
    tk.Label(top, text='项目', bg=BG, fg=SUB, font=FONT_SM).pack(side='left')
    projects = ['全部'] + sorted(set(r.get('project', '') for r in all_records))
    cb = ttk.Combobox(top, textvariable=proj_var, values=projects,
                      width=28, state='readonly', font=FONT)
    cb.pack(side='left', padx=(6, 0))
    return cb


def build_list(parent):
    cols = ('时间', '项目', '内容')
    tree = ttk.Treeview(parent, columns=cols, show='headings', selectmode='extended')
    for col, w in zip(cols, (155, 210, 360)):
        tree.heading(col, text=col if col != '内容' else '内容摘要')
        tree.column(col, width=w, anchor='w')
    sb = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')
    return tree


def build_detail(parent):
    txt = tk.Text(parent, bg=CARD, fg=TEXT, font=FONT, relief='flat',
                  wrap='word', state='disabled', padx=12, pady=10,
                  selectbackground=ACCENT, selectforeground='#FFFFFF')
    sb = ttk.Scrollbar(parent, orient='vertical', command=txt.yview)
    txt.configure(yscrollcommand=sb.set)
    txt.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')
    return txt
