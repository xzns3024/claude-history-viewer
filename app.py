import tkinter as tk
import os
from ui import apply_style, set_theme, get_theme, theme
from ui import ACCENT, ACCENT2, FONT, FONT_SM, FONT_BOLD, FONT_H2
from tabs.history import HistoryTab
from tabs.sessions import SessionsTab
from tabs.stats import StatsTab
from tabs.tasks import TasksTab
from tabs.config import ConfigTab
from tabs.debug import DebugTab
from tabs.filehistory import FileHistoryTab
from tabs.cleanup import CleanupTab

NAV_ITEMS = [
    ('历史记录', '📋', HistoryTab),
    ('会话记录', '💬', SessionsTab),
    ('使用统计', '📊', StatsTab),
    ('任务管理', '✅', TasksTab),
    ('配置管理', '⚙',  ConfigTab),
    ('调试日志', '🐛', DebugTab),
    ('文件历史', '📁', FileHistoryTab),
    ('缓存清理', '🧹', CleanupTab),
]


class SidebarBtn(tk.Frame):
    def __init__(self, parent, icon, label, command):
        t = theme()
        super().__init__(parent, bg=t['SIDEBAR_BG'], cursor='hand2')
        self.command = command
        self.active = False
        self._icon = icon
        self._label = label

        self.indicator = tk.Frame(self, bg=t['SIDEBAR_BG'], width=3)
        self.indicator.pack(side='left', fill='y')

        inner = tk.Frame(self, bg=t['SIDEBAR_BG'], pady=10, padx=12)
        inner.pack(side='left', fill='both', expand=True)

        self.icon_lbl = tk.Label(inner, text=icon, bg=t['SIDEBAR_BG'],
                                 fg=t['SIDEBAR_FG'],
                                 font=('Microsoft YaHei UI', 13),
                                 width=2, anchor='center')
        self.icon_lbl.pack(side='left')
        self.text_lbl = tk.Label(inner, text=label, bg=t['SIDEBAR_BG'],
                                 fg=t['SIDEBAR_FG'],
                                 font=('Microsoft YaHei UI', 10))
        self.text_lbl.pack(side='left', padx=(8, 0))

        for w in (self, inner, self.icon_lbl, self.text_lbl):
            w.bind('<Button-1>', lambda _: self.command())
            w.bind('<Enter>', self._on_enter)
            w.bind('<Leave>', self._on_leave)

    def _on_enter(self, _):
        if not self.active:
            t = theme()
            self._set_colors(t['SIDEBAR_ACT'], '#C5CCE0')

    def _on_leave(self, _):
        if not self.active:
            t = theme()
            self._set_colors(t['SIDEBAR_BG'], t['SIDEBAR_FG'])

    def _set_colors(self, bg, fg):
        t = theme()
        self.config(bg=bg)
        for w in self.winfo_children():
            w.config(bg=bg)
            for c in w.winfo_children():
                c.config(bg=bg, fg=fg if hasattr(c, 'cget') and 'fg' in c.keys() else fg)
        self.indicator.config(bg=bg)

    def set_active(self, active):
        self.active = active
        t = theme()
        if active:
            self.indicator.config(bg=ACCENT)
            self._set_colors(t['SIDEBAR_ACT'], '#FFFFFF')
        else:
            self.indicator.config(bg=t['SIDEBAR_BG'])
            self._set_colors(t['SIDEBAR_BG'], t['SIDEBAR_FG'])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Claude .claude 管理器')
        self.geometry('1300x780')
        self.minsize(900, 560)
        self.protocol('WM_DELETE_WINDOW', self._quit)
        set_theme('light')
        apply_style()
        self._build()
        self._switch(0)

    def _build(self):
        t = theme()
        self.configure(bg=t['BG'])

        # 清空旧内容
        for w in self.winfo_children():
            w.destroy()

        self._current = -1
        self._tab_cache = {}
        self._nav_btns = []

        # 侧边栏
        sidebar = tk.Frame(self, bg=t['SIDEBAR_BG'], width=180)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # Logo 区
        logo_frame = tk.Frame(sidebar, bg=t['SIDEBAR_BG'], pady=20, padx=16)
        logo_frame.pack(fill='x')
        tk.Label(logo_frame, text='Claude', bg=t['SIDEBAR_BG'],
                 fg='#FFFFFF', font=('Microsoft YaHei UI', 14, 'bold')).pack(side='left')
        tk.Label(logo_frame, text=' 管理器', bg=t['SIDEBAR_BG'],
                 fg=t['SIDEBAR_FG'], font=('Microsoft YaHei UI', 10)).pack(side='left')

        tk.Frame(sidebar, bg='#2D3A52', height=1).pack(fill='x', padx=12)

        # 导航按钮
        nav_frame = tk.Frame(sidebar, bg=t['SIDEBAR_BG'])
        nav_frame.pack(fill='x', pady=(8, 0))

        for i, (name, icon, cls) in enumerate(NAV_ITEMS):
            btn = SidebarBtn(nav_frame, icon, name,
                             command=lambda idx=i: self._switch(idx))
            btn.pack(fill='x')
            self._nav_btns.append(btn)

        # 底部主题切换
        tk.Frame(sidebar, bg='#2D3A52', height=1).pack(fill='x', padx=12, side='bottom', pady=(0, 8))
        theme_frame = tk.Frame(sidebar, bg=t['SIDEBAR_BG'])
        theme_frame.pack(side='bottom', fill='x', padx=12, pady=8)

        tk.Label(theme_frame, text='主题', bg=t['SIDEBAR_BG'],
                 fg=t['SIDEBAR_FG'],
                 font=('Microsoft YaHei UI', 8)).pack(anchor='w', pady=(0, 4))

        btn_row = tk.Frame(theme_frame, bg=t['SIDEBAR_BG'])
        btn_row.pack(fill='x')

        is_light = get_theme() == 'light'
        light_bg = ACCENT if is_light else '#2D3A52'
        dark_bg  = ACCENT if not is_light else '#2D3A52'

        self._light_btn = tk.Button(btn_row, text='☀ 白',
                                    font=('Microsoft YaHei UI', 9),
                                    bg=light_bg, fg='#FFFFFF',
                                    relief='flat', cursor='hand2',
                                    padx=10, pady=4,
                                    command=lambda: self._switch_theme('light'))
        self._light_btn.pack(side='left', expand=True, fill='x', padx=(0, 4))

        self._dark_btn = tk.Button(btn_row, text='🌙 黑',
                                   font=('Microsoft YaHei UI', 9),
                                   bg=dark_bg, fg='#FFFFFF',
                                   relief='flat', cursor='hand2',
                                   padx=10, pady=4,
                                   command=lambda: self._switch_theme('dark'))
        self._dark_btn.pack(side='left', expand=True, fill='x')

        # 右侧内容区
        self.content = tk.Frame(self, bg=t['BG'])
        self.content.pack(side='left', fill='both', expand=True)

        # 顶部标题栏
        header = tk.Frame(self.content, bg=t['HEADER_BG'], height=48)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Frame(header, bg=t['BORDER'], height=1).pack(side='bottom', fill='x')

        self.header_icon = tk.Label(header, text='', bg=t['HEADER_BG'],
                                    fg=ACCENT, font=('Microsoft YaHei UI', 14))
        self.header_icon.pack(side='left', padx=(20, 6), pady=8)
        self.header_title = tk.Label(header, bg=t['HEADER_BG'], fg=t['HEADER_FG'],
                                     font=('Microsoft YaHei UI', 12, 'bold'))
        self.header_title.pack(side='left', pady=10)

        # Tab 容器
        self.tab_container = tk.Frame(self.content, bg=t['BG'])
        self.tab_container.pack(fill='both', expand=True)

    def _switch_theme(self, name):
        if get_theme() == name:
            return
        cur = self._current
        set_theme(name)
        apply_style()
        # 先强制销毁所有子组件并刷新
        for w in self.winfo_children():
            w.destroy()
        self.update_idletasks()
        self._build()
        self.update_idletasks()
        self._switch(cur)

    def _switch(self, idx):
        if idx == self._current:
            return
        if self._current >= 0:
            self._nav_btns[self._current].set_active(False)
        self._nav_btns[idx].set_active(True)
        self._current = idx

        name, icon, cls = NAV_ITEMS[idx]
        self.header_icon.config(text=icon)
        self.header_title.config(text=name)

        for w in self.tab_container.winfo_children():
            w.pack_forget()

        if idx not in self._tab_cache:
            try:
                tab = cls(self.tab_container)
            except Exception as e:
                tab = tk.Frame(self.tab_container, bg=theme()['BG'])
                tk.Label(tab, text=f'{name} 加载失败：{e}',
                         bg=theme()['BG'], fg='#FF4D4F',
                         font=('Microsoft YaHei UI', 10)).pack(expand=True)
            self._tab_cache[idx] = tab

        self._tab_cache[idx].pack(fill='both', expand=True)

    def _quit(self):
        self.destroy()
        os._exit(0)


if __name__ == '__main__':
    app = App()
    app.mainloop()
