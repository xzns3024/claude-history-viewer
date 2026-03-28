import json
import os
import tkinter as tk
from tkinter import messagebox
from data import CLAUDE_DIR
from ui import BG, CARD, TEXT, SUB, ACCENT, FONT, FONT_SM

SETTINGS_FILE = os.path.join(CLAUDE_DIR, 'settings.json')
CLAUDE_MD = os.path.join(CLAUDE_DIR, 'CLAUDE.md')


class ConfigTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._current_file = None
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=BG, pady=10)
        top.pack(fill='x', padx=16)
        tk.Button(top, text='settings.json', font=FONT_SM, bg=ACCENT, fg='white',
                  relief='flat', padx=12, pady=4, cursor='hand2',
                  command=lambda: self._load(SETTINGS_FILE)).pack(side='left', padx=(0, 8))
        tk.Button(top, text='CLAUDE.md', font=FONT_SM, bg='#5C2D91', fg='white',
                  relief='flat', padx=12, pady=4, cursor='hand2',
                  command=lambda: self._load(CLAUDE_MD)).pack(side='left', padx=(0, 20))
        self.file_label = tk.Label(top, bg=BG, fg=SUB, font=FONT_SM, text='点击左侧按钮选择文件')
        self.file_label.pack(side='left')
        tk.Button(top, text='保存', font=FONT_SM, bg='#107C10', fg='white',
                  relief='flat', padx=16, pady=4, cursor='hand2',
                  command=self._save).pack(side='right')

        tk.Frame(self, bg='#E0E0E0', height=1).pack(fill='x')

        self.editor = tk.Text(self, bg=CARD, fg=TEXT, font=('Consolas', 10),
                              relief='flat', wrap='none', padx=12, pady=10,
                              insertbackground=ACCENT, undo=True)
        sb_y = tk.Scrollbar(self, orient='vertical', command=self.editor.yview)
        sb_x = tk.Scrollbar(self, orient='horizontal', command=self.editor.xview)
        self.editor.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side='right', fill='y')
        sb_x.pack(side='bottom', fill='x')
        self.editor.pack(fill='both', expand=True, padx=0)

        self._load(SETTINGS_FILE)

    def _load(self, path):
        self._current_file = path
        self.file_label.config(text=path)
        self.editor.delete('1.0', 'end')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if path.endswith('.json'):
                    try:
                        content = json.dumps(json.loads(content), ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                self.editor.insert('end', content)
            except Exception as e:
                self.editor.insert('end', f'读取失败: {e}')
        else:
            self.editor.insert('end', f'文件不存在: {path}')

    def _save(self):
        if not self._current_file:
            return
        content = self.editor.get('1.0', 'end-1c')
        if self._current_file.endswith('.json'):
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                messagebox.showerror('JSON 格式错误', str(e))
                return
        try:
            with open(self._current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo('保存成功', f'已保存到 {self._current_file}')
        except Exception as e:
            messagebox.showerror('保存失败', str(e))
