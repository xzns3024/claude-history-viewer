import tkinter as tk
from tkinter import ttk

# ── 主题定义 ──────────────────────────────────────────
THEMES = {
    'light': {
        'BG':     '#F0F2F5',
        'CARD':   '#FFFFFF',
        'TEXT':   '#1D2129',
        'TEXT2':  '#4E5969',
        'SUB':    '#86909C',
        'BORDER': '#E5E6EB',
        'HOVER':  '#E8F3FF',
        'SIDEBAR_BG':  '#1C2333',
        'SIDEBAR_ACT': '#2D3A52',
        'SIDEBAR_FG':  '#8B95A8',
        'SIDEBAR_AFG': '#FFFFFF',
        'HEADER_BG':   '#FFFFFF',
        'HEADER_FG':   '#1D2129',
        'TREE_BG':     '#FFFFFF',
        'TREE_HEAD':   '#FAFAFA',
    },
    'dark': {
        'BG':     '#18191C',
        'CARD':   '#242529',
        'TEXT':   '#F0F0F0',
        'TEXT2':  '#C0C0C0',
        'SUB':    '#909090',
        'BORDER': '#3A3B3F',
        'HOVER':  '#2A3A50',
        'SIDEBAR_BG':  '#111215',
        'SIDEBAR_ACT': '#2A3A50',
        'SIDEBAR_FG':  '#B0B8CC',
        'SIDEBAR_AFG': '#FFFFFF',
        'HEADER_BG':   '#242529',
        'HEADER_FG':   '#F0F0F0',
        'TREE_BG':     '#242529',
        'TREE_HEAD':   '#2E2F33',
    },
}

# 当前主题（全局变量，运行时动态切换）
_theme = 'light'

def set_theme(name):
    import importlib, sys
    global _theme, BG, CARD, TEXT, TEXT2, SUB, BORDER, HOVER
    _theme = name
    t = THEMES[name]
    BG     = t['BG']
    CARD   = t['CARD']
    TEXT   = t['TEXT']
    TEXT2  = t['TEXT2']
    SUB    = t['SUB']
    BORDER = t['BORDER']
    HOVER  = t['HOVER']
    # 重载各 tab 模块，使其重新从 ui 取最新颜色变量
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith('tabs.'):
            try:
                importlib.reload(sys.modules[mod_name])
            except Exception:
                pass

def get_theme():
    return _theme

def theme():
    return THEMES[_theme]

# ── 固定配色（不随主题变化）──────────────────────────
ACCENT  = '#1677FF'
ACCENT2 = '#4096FF'
SUCCESS = '#52C41A'
WARN    = '#FA8C16'
DANGER  = '#FF4D4F'

# ── 初始化浅色主题变量 ────────────────────────────────
set_theme('light')

# ── 字体（微软雅黑）──────────────────────────────────
FONT      = ('Microsoft YaHei UI', 10)
FONT_SM   = ('Microsoft YaHei UI', 9)
FONT_BOLD = ('Microsoft YaHei UI', 10, 'bold')
FONT_H1   = ('Microsoft YaHei UI', 13, 'bold')
FONT_H2   = ('Microsoft YaHei UI', 11, 'bold')
FONT_NUM  = ('Microsoft YaHei UI', 20, 'bold')


def apply_style():
    t = theme()
    s = ttk.Style()
    s.theme_use('clam')

    s.configure('Treeview',
                background=t['TREE_BG'], foreground=TEXT,
                fieldbackground=t['TREE_BG'], rowheight=32,
                font=FONT, borderwidth=0, relief='flat')
    s.configure('Treeview.Heading',
                background=t['TREE_HEAD'], foreground=TEXT2,
                font=('Microsoft YaHei UI', 9, 'bold'),
                relief='flat', borderwidth=0, padding=(8, 6))
    s.map('Treeview',
          background=[('selected', ACCENT)],
          foreground=[('selected', '#FFFFFF')])
    s.map('Treeview.Heading',
          background=[('active', HOVER)])

    s.configure('Vertical.TScrollbar',
                troughcolor=BG, background='#C9CDD4',
                arrowsize=12, borderwidth=0, relief='flat')
    s.configure('Horizontal.TScrollbar',
                troughcolor=BG, background='#C9CDD4',
                arrowsize=12, borderwidth=0, relief='flat')
    s.map('Vertical.TScrollbar',
          background=[('active', '#A0A5AD')])

    s.configure('TCombobox', relief='flat',
                fieldbackground=t['TREE_BG'], foreground=TEXT)


def make_label(parent, text, style='normal', **kwargs):
    fonts = {
        'h1': FONT_H1, 'h2': FONT_H2,
        'bold': FONT_BOLD, 'small': FONT_SM,
        'sub': FONT_SM, 'normal': FONT,
    }
    colors = {'sub': SUB, 'h1': TEXT, 'h2': TEXT, 'normal': TEXT,
              'bold': TEXT, 'small': SUB}
    kw = dict(bg=kwargs.pop('bg', BG),
              fg=kwargs.pop('fg', colors.get(style, TEXT)),
              font=fonts.get(style, FONT))
    kw.update(kwargs)
    return tk.Label(parent, text=text, **kw)


def make_separator(parent, **kwargs):
    kwargs.pop('bg', None)
    return tk.Frame(parent, bg=BORDER, height=1, **kwargs)


def make_btn(parent, text, **kwargs):
    cmd = kwargs.pop('command', None)
    padx = kwargs.pop('padx', 14)
    pady = kwargs.pop('pady', 5)
    b = tk.Button(parent, text=text, font=FONT_SM,
                  bg=ACCENT, fg='#FFFFFF',
                  activebackground=ACCENT2, activeforeground='#FFFFFF',
                  relief='flat', cursor='hand2',
                  padx=padx, pady=pady, command=cmd, **kwargs)
    b.bind('<Enter>', lambda e: b.config(bg=ACCENT2))
    b.bind('<Leave>', lambda e: b.config(bg=ACCENT))
    return b


def make_danger_btn(parent, text, **kwargs):
    cmd = kwargs.pop('command', None)
    padx = kwargs.pop('padx', 14)
    pady = kwargs.pop('pady', 5)
    DANGER_DARK = '#D9363E'
    b = tk.Button(parent, text=text, font=FONT_SM,
                  bg=DANGER, fg='#FFFFFF',
                  activebackground=DANGER_DARK, activeforeground='#FFFFFF',
                  relief='flat', cursor='hand2',
                  padx=padx, pady=pady, command=cmd, **kwargs)
    b.bind('<Enter>', lambda e: b.config(bg=DANGER_DARK))
    b.bind('<Leave>', lambda e: b.config(bg=DANGER))
    return b


def build_search_bar(parent, search_var, extra_widgets=None):
    bar = tk.Frame(parent, bg=BG, pady=10)
    bar.pack(fill='x', padx=20)

    search_wrap = tk.Frame(bar, bg=BORDER, padx=1, pady=1)
    search_wrap.pack(side='left')
    inner = tk.Frame(search_wrap, bg=CARD)
    inner.pack()
    tk.Label(inner, text='🔍', bg=CARD, fg=SUB,
             font=FONT_SM).pack(side='left', padx=(6, 2))
    tk.Entry(inner, textvariable=search_var, width=26,
             bg=CARD, fg=TEXT, insertbackground=ACCENT,
             relief='flat', font=FONT,
             highlightthickness=0).pack(side='left', ipady=5, padx=(0, 8))

    if extra_widgets:
        for w_fn in extra_widgets:
            w_fn(bar)
    return bar
