import os
import shutil
import tkinter as tk
from tkinter import messagebox
from data import get_cache_sizes, fmt_size, CLAUDE_DIR
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM

DIR_LABELS = {
    'debug': ('调试日志', 'debug'),
    'file-history': ('文件版本历史', 'file-history'),
    'backups': ('配置备份', 'backups'),
    'cache': ('缓存', 'cache'),
    'paste-cache': ('粘贴缓存', 'paste-cache'),
    'shell-snapshots': ('Shell快照', 'shell-snapshots'),
}


class CleanupTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.vars = {}
        self.size_labels = {}
        self._build()

    def _build(self):
        tk.Label(self, text='选择要清理的目录', bg=BG, fg=TEXT,
                 font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=24, pady=(16, 4))
        tk.Label(self, text='清理后数据无法恢复，请谨慎操作。file-history 清理后将无法撤销 Claude 的编辑。',
                 bg=BG, fg='#C42B1C', font=FONT_SM).pack(anchor='w', padx=24, pady=(0, 12))

        self.card = tk.Frame(self, bg=CARD, bd=0, relief='flat')
        self.card.pack(fill='x', padx=24)

        sizes = get_cache_sizes()
        for key, (label, dirname) in DIR_LABELS.items():
            row = tk.Frame(self.card, bg=CARD, pady=8)
            row.pack(fill='x', padx=16)
            var = tk.BooleanVar(value=False)
            self.vars[key] = var
            tk.Checkbutton(row, variable=var, bg=CARD, activebackground=CARD,
                           cursor='hand2').pack(side='left')
            tk.Label(row, text=label, bg=CARD, fg=TEXT, font=FONT, width=16,
                     anchor='w').pack(side='left')
            path_lbl = tk.Label(row, text=os.path.join(CLAUDE_DIR, dirname),
                                bg=CARD, fg=SUB, font=FONT_SM)
            path_lbl.pack(side='left', padx=(8, 0))
            size_lbl = tk.Label(row, text=fmt_size(sizes.get(key, 0)),
                                bg=CARD, fg=ACCENT, font=('Segoe UI', 10, 'bold'), width=10)
            size_lbl.pack(side='right')
            self.size_labels[key] = size_lbl
            tk.Frame(self.card, bg='#E0E0E0', height=1).pack(fill='x')

        btn_frame = tk.Frame(self, bg=BG, pady=16)
        btn_frame.pack(fill='x', padx=24)
        tk.Button(btn_frame, text='刷新大小', font=FONT_SM, bg=BG, fg=SUB,
                  relief='flat', padx=12, pady=6, cursor='hand2',
                  command=self._refresh).pack(side='left', padx=(0, 12))
        tk.Button(btn_frame, text='全选', font=FONT_SM, bg=BG, fg=SUB,
                  relief='flat', padx=12, pady=6, cursor='hand2',
                  command=lambda: [v.set(True) for v in self.vars.values()]).pack(side='left', padx=(0, 12))
        tk.Button(btn_frame, text='全不选', font=FONT_SM, bg=BG, fg=SUB,
                  relief='flat', padx=12, pady=6, cursor='hand2',
                  command=lambda: [v.set(False) for v in self.vars.values()]).pack(side='left', padx=(0, 24))
        tk.Button(btn_frame, text='清理所选', font=('Segoe UI', 10, 'bold'),
                  bg='#C42B1C', fg='white', activebackground='#A52515',
                  activeforeground='white', relief='flat', padx=20, pady=6,
                  cursor='hand2', command=self._clean).pack(side='right')

        self.result_label = tk.Label(self, bg=BG, fg='#107C10', font=FONT_SM, text='')
        self.result_label.pack(anchor='w', padx=24)

    def _refresh(self):
        sizes = get_cache_sizes()
        for key, lbl in self.size_labels.items():
            lbl.config(text=fmt_size(sizes.get(key, 0)))
        self.result_label.config(text='已刷新')

    def _clean(self):
        selected = [k for k, v in self.vars.items() if v.get()]
        if not selected:
            messagebox.showinfo('提示', '请至少勾选一个目录')
            return
        labels = [DIR_LABELS[k][0] for k in selected]
        if not messagebox.askyesno('确认清理', f'将清理以下目录内容：\n' + '\n'.join(f'  • {l}' for l in labels) + '\n\n此操作不可撤销！'):
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
        self._refresh()
        self.result_label.config(text=f'已释放约 {fmt_size(freed)}')


def _dir_size(path):
    total = 0
    for dp, dns, fns in os.walk(path):
        for f in fns:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except Exception:
                pass
    return total
