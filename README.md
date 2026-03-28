# Claude .claude 管理器

完整的 Claude Code 本地数据管理工具，以图形界面覆盖 `~/.claude` 目录下的所有功能模块。

## 功能模块

| Tab | 说明 |
|-----|------|
| **历史记录** | 浏览/搜索/删除 `history.jsonl` 中的所有输入记录 |
| **会话记录** | 查看 `projects/` 下的完整对话内容（user/assistant 交替展示） |
| **使用统计** | 统计每次会话的 token 用量、时长、工具调用次数、文件修改数 |
| **任务管理** | 查看各会话中通过 TaskCreate 创建的任务及其状态 |
| **配置管理** | 在线查看和编辑 `settings.json` 与 `CLAUDE.md` |
| **调试日志** | 浏览 `debug/` 下的日志文件，支持多选删除 |
| **文件历史** | 浏览 `file-history/` 下的文件版本备份，可查看任意版本内容 |
| **缓存清理** | 统计各缓存目录占用大小，一键选择清理 |

## 环境要求

- Python 3.x
- 仅使用标准库（`tkinter`），无需安装额外依赖

## 运行方式

**Windows 双击运行：**
```
run.bat
```

**命令行运行：**
```bash
python app.py
```

## 目录结构

```
claude-history-viewer-master/
  app.py              # 主窗口，8个Tab容器
  data.py             # 数据加载层（读取各类 .claude 数据）
  ui.py               # 样式与公共UI组件
  tabs/
    history.py        # 历史记录 Tab
    sessions.py       # 会话记录 Tab
    stats.py          # 使用统计 Tab
    tasks.py          # 任务管理 Tab
    config.py         # 配置管理 Tab
    debug.py          # 调试日志 Tab
    filehistory.py    # 文件历史 Tab
    cleanup.py        # 缓存清理 Tab
```

## .claude 目录说明

工具读取的数据均来自 `C:\Users\<用户名>\.claude\`（Windows）或 `~/.claude/`（macOS/Linux）：

| 路径 | 说明 |
|------|------|
| `history.jsonl` | 用户输入历史，每行一条记录 |
| `projects/<proj>/<session>.jsonl` | 完整对话记录，含 user/assistant 消息 |
| `usage-data/session-meta/*.json` | 会话统计数据（token、时长、工具等） |
| `tasks/<session>/*.json` | 任务列表数据 |
| `settings.json` | Claude Code 全局配置 |
| `CLAUDE.md` | 全局指令文件 |
| `debug/*.txt` | 调试日志 |
| `file-history/` | 文件编辑版本备份 |
| `backups/` | 配置文件自动备份 |
| `cache/` | 缓存文件 |
| `paste-cache/` | 粘贴内容缓存 |
| `shell-snapshots/` | Shell 环境快照 |
