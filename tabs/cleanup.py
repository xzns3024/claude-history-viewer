import os
import shutil
import tkinter as tk
from tkinter import messagebox
from data import CLAUDE_DIR, fmt_size
from ui import (BG, CARD, TEXT, TEXT2, SUB, ACCENT, SUCCESS, WARN,
                DANGER, BORDER, FONT, FONT_SM, FONT_BOLD, FONT_NUM,
                FONT_H2, make_separator, make_btn, make_danger_btn)

DIR_LABELS = {
    'debug':           ('调试日志',   'debug'),
    'file-history':    ('文件历史',   'file-history'),
    'backups':         ('备份文件',   'backups'),
    'cache':           ('缓存数据',   'cache'),
    'paste-cache':     ('粘贴缓存',   'paste-cache'),
    'shell-snapshots': ('Shell 快照', 'shell-snapshots'),
}


class CleanupTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.vars = {k: tk.BooleanVar(value=False) for k in DIR_LABELS}
        self.size_labels = {}
        self._build()
        self._refresh()

    def _build(self):
        toolbar = tk.Frame(self, bg=BG, pady=14)
        toolbar.pack(fill='x', padx=20)
        tk.Label(toolbar, text='缓存清理', bg=BG, fg=TEXT,
                 font=FONT_BOLD).pack(side='left')
        self.result_label = tk.Label(toolbar, text='', bg=BG,
                                     fg=SUCCESS, font=FONT_SM)
        self.result_label.pack(side='left', padx=16)
        make_btn(toolbar, '刷新大小', padx=12, pady=5,
                 command=self._refresh).pack(side='right', padx=(6, 0))
        make_danger_btn(toolbar, '执行清理', padx=12, pady=5,
                        command=self._clean).pack(side='right')

        make_separator(self).pack(fill='x')

        # 卡片区域
        content = tk.Frame(self, bg=BG)
        content.pack(fill='both', expand=True, padx=24, pady=20)

        # 全选控制行
        ctrl = tk.Frame(content, bg=BG, pady=4)
        ctrl.pack(fill='x')
        tk.Label(ctrl, text='选择要清理的目录：', bg=BG,
                 fg=TEXT2, font=FONT_SM).pack(side='left')
        tk.Button(ctrl, text='全选', font=FONT_SM,
                  bg=BG, fg=ACCENT, relief='flat',
                  cursor='hand2', padx=0,
                  command=self._select_all).pack(side='left', padx=(12, 4))
        tk.Button(ctrl, text='取消全选', font=FONT_SM,
                  bg=BG, fg=SUB, relief='flat',
                  cursor='hand2', padx=0,
                  command=self._deselect_all).pack(side='left')

        # 目录列表（单一 grid 容器，所有行共享列宽）
        table = tk.Frame(content, bg=BG)
        table.pack(fill='x')
        table.grid_columnconfigure(0, minsize=130)  # 勾选框列
        table.grid_columnconfigure(1, weight=1)     # 路径列（自动伸展）
        table.grid_columnconfigure(2, minsize=90)   # 大小列

        for row_idx, (key, (label, dirname)) in enumerate(DIR_LABELS.items()):
            bg = CARD
            pad_y = (6, 0) if row_idx == 0 else (0, 0)

            cb = tk.Checkbutton(table, variable=self.vars[key],
                                bg=bg, activebackground=bg,
                                fg=TEXT, font=FONT,
                                text=label, cursor='hand2', anchor='w')
            cb.grid(row=row_idx, column=0, sticky='w', padx=(4, 0), pady=4)

            path_lbl = tk.Label(table, text=f'.claude/{dirname}',
                                bg=bg, fg=SUB, font=FONT_SM, anchor='w')
            path_lbl.grid(row=row_idx, column=1, sticky='w', padx=(8, 0), pady=4)

            size_lbl = tk.Label(table, text='--',
                                bg=bg, fg=WARN, font=FONT_BOLD, anchor='e')
            size_lbl.grid(row=row_idx, column=2, sticky='e', padx=(0, 8), pady=4)
            self.size_labels[key] = size_lbl

    def _select_all(self):
        for v in self.vars.values():
            v.set(True)

    def _deselect_all(self):
        for v in self.vars.values():
            v.set(False)

    def _refresh(self):
        for key, (_, dirname) in DIR_LABELS.items():
            path = os.path.join(CLAUDE_DIR, dirname)
            size = _dir_size(path)
            color = DANGER if size > 10 * 1024 * 1024 else \
                    WARN   if size > 1  * 1024 * 1024 else SUB
            self.size_labels[key].config(text=fmt_size(size), fg=color)
        self.result_label.config(text='已刷新', fg=SUCCESS)

    def _clean(self):
        selected = [k for k, v in self.vars.items() if v.get()]
        if not selected:
            messagebox.showinfo('提示', '请至少勾选一个目录')
            return
        labels = [DIR_LABELS[k][0] for k in selected]
        msg = '将清理以下目录内容：\n' + \
              '\n'.join(f'  · {l}' for l in labels) + \
              '\n\n此操作不可撤销！'
        if not messagebox.askyesno('确认清理', msg):
            return
        freed = 0
        for key in selected:
            dirname = DIR_LABELS[key][1]
            path = os.path.join(CLAUDE_DIR, dirname)
            if os.path.exists(path):
                freed += _dir_size(path)
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except Exception:
                        pass
        self._deselect_all()
        self._refresh()
        self.result_label.config(
            text=f'已释放 {fmt_size(freed)}', fg=SUCCESS)


def _dir_size(path):
    total = 0
    if not os.path.exists(path):
        return 0
    for dp, _, fns in os.walk(path):
        for f in fns:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except Exception:
                pass
    return total
