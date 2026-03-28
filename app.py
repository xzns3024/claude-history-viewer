import tkinter as tk
from tkinter import ttk
from ui import apply_style, BG
from tabs.history import HistoryTab
from tabs.sessions import SessionsTab
from tabs.stats import StatsTab
from tabs.tasks import TasksTab
from tabs.config import ConfigTab
from tabs.debug import DebugTab
from tabs.filehistory import FileHistoryTab
from tabs.cleanup import CleanupTab
import os


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Claude .claude 管理器')
        self.geometry('1280x760')
        self.configure(bg=BG)
        self.minsize(900, 560)
        self.protocol('WM_DELETE_WINDOW', self._quit)
        apply_style()
        self._build_notebook()

    def _build_notebook(self):
        style = ttk.Style()
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', font=('Segoe UI', 10), padding=(14, 6))
        style.map('TNotebook.Tab',
                  background=[('selected', '#FFFFFF'), ('!selected', '#E0E0E0')],
                  foreground=[('selected', '#0078D4'), ('!selected', '#605E5C')])

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)

        tabs = [
            ('历史记录', HistoryTab),
            ('会话记录', SessionsTab),
            ('使用统计', StatsTab),
            ('任务管理', TasksTab),
            ('配置管理', ConfigTab),
            ('调试日志', DebugTab),
            ('文件历史', FileHistoryTab),
            ('缓存清理', CleanupTab),
        ]
        for name, TabClass in tabs:
            try:
                frame = TabClass(nb)
                nb.add(frame, text=f'  {name}  ')
            except Exception as e:
                err = tk.Frame(nb, bg=BG)
                tk.Label(err, text=f'{name} 加载失败：{e}', bg=BG, fg='#C42B1C',
                         font=('Segoe UI', 10)).pack(expand=True)
                nb.add(err, text=f'  {name}  ')

    def _quit(self):
        self.destroy()
        os._exit(0)


if __name__ == '__main__':
    app = App()
    app.mainloop()
