"""学习数据存储（SQLite）。

只存三类东西：
1. 学习进度（已读知识点、已通过题目、经验值……）——整份存成 JSON，简单不易出错。
2. 提交记录 + 错题本。
3. AI 调用缓存与每日用量（省钱用的）。

全部放在 backend/data/dsquest.db，删掉这个文件就等于重置进度。
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from datetime import date
from typing import Any

from .config import DATA_DIR, DB_PATH

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id TEXT NOT NULL,
    lang TEXT NOT NULL,
    code TEXT NOT NULL,
    verdict TEXT NOT NULL,
    passed INTEGER NOT NULL,
    total INTEGER NOT NULL,
    time_ms INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wrongbook (
    problem_id TEXT PRIMARY KEY,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_verdict TEXT NOT NULL,
    last_reason TEXT DEFAULT '',
    first_failed_at TEXT NOT NULL,
    last_failed_at TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0,
    note TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS ai_cache (
    cache_key TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_usage (
    day TEXT PRIMARY KEY,
    calls INTEGER NOT NULL DEFAULT 0
);
"""


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _lock, connect() as conn:
        conn.executescript(SCHEMA)


# ------------------------------------------------------------------ progress
DEFAULT_PROGRESS: dict[str, Any] = {
    "xp": 0,
    "knowledgeRead": [],   # ["linear-list/seqlist-basic", ...]
    "problemsSolved": [],  # ["ll-01", ...]
    "moduleCleared": [],   # ["linear-list", ...]
    "streakDays": 0,
    "lastActiveDay": "",
    "quizCorrect": 0,
}


def get_progress() -> dict[str, Any]:
    with _lock, connect() as conn:
        row = conn.execute("SELECT value FROM kv WHERE key = 'progress'").fetchone()
    if not row:
        return json.loads(json.dumps(DEFAULT_PROGRESS))
    data = json.loads(row["value"])
    merged = json.loads(json.dumps(DEFAULT_PROGRESS))
    merged.update(data)
    return merged


def save_progress(progress: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps(progress, ensure_ascii=False)
    with _lock, connect() as conn:
        conn.execute(
            "INSERT INTO kv(key, value, updated_at) VALUES('progress', ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            (payload, _now()),
        )
    return progress


def add_xp(amount: int) -> dict[str, Any]:
    progress = get_progress()
    progress["xp"] = int(progress.get("xp", 0)) + amount
    return save_progress(progress)


# --------------------------------------------------------------- submissions
def record_submission(
    problem_id: str,
    lang: str,
    code: str,
    verdict: str,
    passed: int,
    total: int,
    time_ms: int,
) -> int:
    with _lock, connect() as conn:
        cur = conn.execute(
            "INSERT INTO submissions(problem_id, lang, code, verdict, passed, total, time_ms, created_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (problem_id, lang, code, verdict, passed, total, time_ms, _now()),
        )
        return int(cur.lastrowid)


def recent_submissions(limit: int = 20) -> list[dict[str, Any]]:
    with _lock, connect() as conn:
        rows = conn.execute(
            "SELECT id, problem_id, lang, verdict, passed, total, time_ms, created_at"
            " FROM submissions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def last_code(problem_id: str) -> dict[str, Any] | None:
    with _lock, connect() as conn:
        row = conn.execute(
            "SELECT code, lang, created_at FROM submissions WHERE problem_id = ? ORDER BY id DESC LIMIT 1",
            (problem_id,),
        ).fetchone()
    return dict(row) if row else None


# ----------------------------------------------------------------- wrongbook
def touch_wrong(problem_id: str, verdict: str, reason: str) -> None:
    now = _now()
    with _lock, connect() as conn:
        conn.execute(
            "INSERT INTO wrongbook(problem_id, attempts, last_verdict, last_reason, first_failed_at,"
            " last_failed_at, resolved) VALUES (?,1,?,?,?,?,0) "
            "ON CONFLICT(problem_id) DO UPDATE SET attempts = attempts + 1,"
            " last_verdict = excluded.last_verdict, last_reason = excluded.last_reason,"
            " last_failed_at = excluded.last_failed_at, resolved = 0",
            (problem_id, verdict, reason, now, now),
        )


def resolve_wrong(problem_id: str) -> None:
    with _lock, connect() as conn:
        conn.execute("UPDATE wrongbook SET resolved = 1 WHERE problem_id = ?", (problem_id,))


def list_wrong() -> list[dict[str, Any]]:
    with _lock, connect() as conn:
        rows = conn.execute(
            "SELECT * FROM wrongbook ORDER BY resolved ASC, last_failed_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def set_note(problem_id: str, note: str) -> None:
    with _lock, connect() as conn:
        conn.execute("UPDATE wrongbook SET note = ? WHERE problem_id = ?", (note, problem_id))


# ------------------------------------------------------------------------ AI
def ai_cache_get(key: str) -> dict[str, Any] | None:
    with _lock, connect() as conn:
        row = conn.execute("SELECT payload FROM ai_cache WHERE cache_key = ?", (key,)).fetchone()
    return json.loads(row["payload"]) if row else None


def ai_cache_put(key: str, payload: dict[str, Any]) -> None:
    with _lock, connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO ai_cache(cache_key, payload, created_at) VALUES (?,?,?)",
            (key, json.dumps(payload, ensure_ascii=False), _now()),
        )


def ai_usage_today() -> int:
    today = date.today().isoformat()
    with _lock, connect() as conn:
        row = conn.execute("SELECT calls FROM ai_usage WHERE day = ?", (today,)).fetchone()
    return int(row["calls"]) if row else 0


def ai_usage_inc() -> int:
    today = date.today().isoformat()
    with _lock, connect() as conn:
        conn.execute(
            "INSERT INTO ai_usage(day, calls) VALUES (?, 1) "
            "ON CONFLICT(day) DO UPDATE SET calls = calls + 1",
            (today,),
        )
        row = conn.execute("SELECT calls FROM ai_usage WHERE day = ?", (today,)).fetchone()
    return int(row["calls"])
