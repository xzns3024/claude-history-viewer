import json
import os
from datetime import datetime

CLAUDE_DIR = os.path.join(os.path.expanduser('~'), '.claude')
HISTORY_FILE = os.path.join(CLAUDE_DIR, 'history.jsonl')


def format_time(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')


def format_iso(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return iso_str


def load_history():
    records = []
    if not os.path.exists(HISTORY_FILE):
        return records
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def load_sessions():
    """扫描 projects/ 下所有 .jsonl，返回会话列表"""
    projects_dir = os.path.join(CLAUDE_DIR, 'projects')
    sessions = []
    if not os.path.exists(projects_dir):
        return sessions
    for proj in os.listdir(projects_dir):
        proj_path = os.path.join(projects_dir, proj)
        if not os.path.isdir(proj_path):
            continue
        for fname in os.listdir(proj_path):
            if not fname.endswith('.jsonl'):
                continue
            fpath = os.path.join(proj_path, fname)
            session_id = fname[:-6]
            mtime = os.path.getmtime(fpath)
            size = os.path.getsize(fpath)
            sessions.append({
                'project': proj,
                'session_id': session_id,
                'path': fpath,
                'mtime': mtime,
                'size': size,
            })
    sessions.sort(key=lambda x: x['mtime'], reverse=True)
    return sessions


def load_session_messages(path):
    """读取单个会话 .jsonl，返回消息列表"""
    messages = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if obj.get('type') in ('user', 'assistant'):
                        messages.append(obj)
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass
    return messages


def load_usage_stats():
    """读取 usage-data/session-meta/ 下所有 json"""
    meta_dir = os.path.join(CLAUDE_DIR, 'usage-data', 'session-meta')
    stats = []
    if not os.path.exists(meta_dir):
        return stats
    for fname in os.listdir(meta_dir):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(meta_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats.append(data)
        except Exception:
            pass
    stats.sort(key=lambda x: x.get('start_time', ''), reverse=True)
    return stats


def load_tasks():
    """读取 tasks/ 下所有 session 的任务"""
    tasks_dir = os.path.join(CLAUDE_DIR, 'tasks')
    all_tasks = []
    if not os.path.exists(tasks_dir):
        return all_tasks
    for session_id in os.listdir(tasks_dir):
        session_path = os.path.join(tasks_dir, session_id)
        if not os.path.isdir(session_path):
            continue
        for fname in os.listdir(session_path):
            if not fname.endswith('.json'):
                continue
            fpath = os.path.join(session_path, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    task = json.load(f)
                    task['_session_id'] = session_id
                    all_tasks.append(task)
            except Exception:
                pass
    return all_tasks


def load_debug_files():
    """列出 debug/ 下所有文件"""
    debug_dir = os.path.join(CLAUDE_DIR, 'debug')
    files = []
    if not os.path.exists(debug_dir):
        return files
    for fname in os.listdir(debug_dir):
        fpath = os.path.join(debug_dir, fname)
        if os.path.isfile(fpath):
            files.append({
                'name': fname,
                'path': fpath,
                'size': os.path.getsize(fpath),
                'mtime': os.path.getmtime(fpath),
            })
    files.sort(key=lambda x: x['mtime'], reverse=True)
    return files


def load_file_history():
    """列出 file-history/ 结构，返回 {session_id: [版本文件名列表]}"""
    fh_dir = os.path.join(CLAUDE_DIR, 'file-history')
    result = []
    if not os.path.exists(fh_dir):
        return result
    for session_id in os.listdir(fh_dir):
        session_path = os.path.join(fh_dir, session_id)
        if not os.path.isdir(session_path):
            continue
        versions = []
        for vname in os.listdir(session_path):
            vpath = os.path.join(session_path, vname)
            versions.append({
                'name': vname,
                'path': vpath,
                'size': os.path.getsize(vpath),
            })
        result.append({'session_id': session_id, 'versions': versions})
    return result


def get_dir_size(path):
    """递归计算目录大小（字节）"""
    total = 0
    if not os.path.exists(path):
        return 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except Exception:
                pass
    return total


def get_cache_sizes():
    """统计各可清理目录的大小"""
    targets = {
        'debug': os.path.join(CLAUDE_DIR, 'debug'),
        'file-history': os.path.join(CLAUDE_DIR, 'file-history'),
        'backups': os.path.join(CLAUDE_DIR, 'backups'),
        'cache': os.path.join(CLAUDE_DIR, 'cache'),
        'paste-cache': os.path.join(CLAUDE_DIR, 'paste-cache'),
        'shell-snapshots': os.path.join(CLAUDE_DIR, 'shell-snapshots'),
    }
    return {k: get_dir_size(v) for k, v in targets.items()}


def fmt_size(b):
    """字节转可读字符串"""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if b < 1024:
            return f'{b:.1f} {unit}'
        b /= 1024
    return f'{b:.1f} TB'
