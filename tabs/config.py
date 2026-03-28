import json
import tkinter as tk
from tkinter import ttk, messagebox
import os, json
from data import CLAUDE_DIR

def load_configs():
    result = []
    for fname in ('settings.json', 'settings.local.json', '.claude.json'):
        fpath = os.path.join(CLAUDE_DIR, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    result.append({'name': fname, 'path': fpath, 'data': json.load(f)})
            except Exception:
                result.append({'name': fname, 'path': fpath, 'data': {}})
    return result
from ui import (BG, CARD, TEXT, TEXT2, SUB, ACCENT, BORDER,
                FONT, FONT_SM, FONT_BOLD, FONT_H2,
                make_separator, make_btn, make_danger_btn)


class ConfigTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.configs = load_configs()
        self._build()

    def _build(self):
        toolbar = tk.Frame(self, bg=BG, pady=14)
        toolbar.pack(fill='x', padx=20)
        tk.Label(toolbar, text=f'共 {len(self.configs)} 个配置文件',
                 bg=BG, fg=SUB, font=FONT_SM).pack(side='left')
        make_btn(toolbar, '保存修改', padx=12, pady=5,
                 command=self._save).pack(side='right')

        make_separator(self).pack(fill='x')

        pane = tk.PanedWindow(self, orient='horizontal', bg=BG,
                              sashwidth=5, sashrelief='flat', bd=0)
        pane.pack(fill='both', expand=True)

        left = tk.Frame(pane, bg=BG)
        self._build_list(left)
        pane.add(left, minsize=260)

        right = tk.Frame(pane, bg=CARD)
        self._build_editor(right)
        pane.add(right, minsize=400)

        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        if self.configs:
            first = self.tree.get_children()[0]
            self.tree.selection_set(first)
            self.tree.focus(first)

    def _build_list(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(frame, columns=('文件',),
                                  show='headings', selectmode='browse')
        self.tree.heading('文件', text='配置文件')
        self.tree.column('文件', width=240, anchor='w', stretch=True)
        sb = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        odd_bg = '#F7F8FA' if BG == '#F0F2F5' else '#2A2B2F'
        self.tree.tag_configure('odd',  background=odd_bg)
        self.tree.tag_configure('even', background=CARD)

        for i, cfg in enumerate(self.configs):
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end',
                             values=(cfg.get('name', ''),),
                             tags=(tag, str(i)))

    def _build_editor(self, parent):
        header = tk.Frame(parent, bg=CARD, pady=10, padx=16)
        header.pack(fill='x')
        self.file_label = tk.Label(header, text='选择左侧配置文件进行编辑',
                                   bg=CARD, fg=TEXT2, font=FONT_BOLD)
        self.file_label.pack(side='left')
        make_separator(parent, bg=BORDER).pack(fill='x')

        self.editor = tk.Text(parent, bg=CARD, fg=TEXT,
                              font=('Consolas', 10),
                              relief='flat', wrap='none',
                              insertbackground=ACCENT,
                              padx=16, pady=12)
        sb_y = ttk.Scrollbar(parent, orient='vertical',
                             command=self.editor.yview)
        sb_x = ttk.Scrollbar(parent, orient='horizontal',
                             command=self.editor.xview)
        self.editor.configure(yscrollcommand=sb_y.set,
                              xscrollcommand=sb_x.set)
        self.editor.pack(side='left', fill='both', expand=True)
        sb_y.pack(side='right', fill='y')

        self._current_path = None

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], 'tags')
        idx = next((t for t in tags if t.isdigit()), None)
        if idx is None:
            return
        cfg = self.configs[int(idx)]
        self._current_path = cfg.get('path', '')
        self.file_label.config(text=cfg.get('name', ''))
        self.editor.delete('1.0', 'end')
        try:
            with open(self._current_path, 'r',
                      encoding='utf-8', errors='replace') as f:
                content = f.read()
            try:
                obj = json.loads(content)
                content = json.dumps(obj, ensure_ascii=False, indent=2)
            except Exception:
                pass
            self.editor.insert('end', content)
        except Exception as e:
            self.editor.insert('end', f'读取失败: {e}')

    def _save(self):
        if not self._current_path:
            messagebox.showinfo('提示', '请先选择配置文件')
            return
        content = self.editor.get('1.0', 'end-1c')
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            messagebox.showerror('JSON 格式错误', str(e))
            return
        try:
            with open(self._current_path, 'w',
                      encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo('成功', '配置已保存')
        except Exception as e:
            messagebox.showerror('保存失败', str(e))
