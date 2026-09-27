"""
SQLite-backed persistence layer for YouTube Shorts deduplication and history.
Enables WAL mode for concurrency and zero lockups between CLI & Web Studio.
"""

import sqlite3
import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from src.core.config import DATA_DIR

DB_PATH = DATA_DIR / "shorts_history.db"


def get_db_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def init_db():
    """Initializes tables and indexes."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shorts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                niche_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                hook TEXT,
                voice_id TEXT,
                mode TEXT NOT NULL,
                script_json TEXT,
                video_path TEXT,
                youtube_video_id TEXT,
                status TEXT DEFAULT 'generated',
                title TEXT,
                description TEXT,
                error_message TEXT
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_niche_topic ON shorts(niche_id, topic);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON shorts(status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON shorts(created_at);")
        conn.commit()


def record_short(
    session_id: str,
    niche_id: str,
    topic: str,
    hook: str,
    voice_id: str,
    mode: str,
    script_data: Dict[str, Any],
    video_path: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: str = "generated",
) -> int:
    """Inserts a new generated Short into history."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO shorts (
                session_id, niche_id, topic, hook, voice_id, mode,
                script_json, video_path, title, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                niche_id,
                topic,
                hook,
                voice_id,
                mode,
                json.dumps(script_data),
                video_path,
                title,
                description,
                status,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def update_short_status(
    session_id: str,
    status: str,
    youtube_video_id: Optional[str] = None,
    error_message: Optional[str] = None,
):
    """Updates status and upload metadata for a specific short."""
    with get_db_connection() as conn:
        conn.execute(
            """
            UPDATE shorts
            SET status = ?,
                youtube_video_id = COALESCE(?, youtube_video_id),
                error_message = ?
            WHERE session_id = ?
            """,
            (status, youtube_video_id, error_message, session_id),
        )
        conn.commit()


def get_recent_topics(niche_id: str, limit: int = 30) -> List[str]:
    """Returns the last `limit` topics covered in this niche to prevent repeats."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT topic FROM shorts WHERE niche_id = ? ORDER BY id DESC LIMIT ?",
            (niche_id, limit),
        )
        return [row["topic"] for row in cursor.fetchall()]


def get_all_shorts(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Returns a list of all shorts with pagination for the Web Studio."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM shorts ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        results = []
        for r in cursor.fetchall():
            d = dict(r)
            if d.get("script_json"):
                try:
                    d["script_data"] = json.loads(d["script_json"])
                except Exception:
                    d["script_data"] = None
            results.append(d)
        return results


def get_short_by_session_id(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single Short by session ID."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM shorts WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("script_json"):
            try:
                d["script_data"] = json.loads(d["script_json"])
            except Exception:
                d["script_data"] = None
        return d


def count_today_uploads() -> int:
    """Counts number of videos uploaded in the past 24 hours."""
    init_db()
    cutoff = datetime.now(timezone.utc).strftime("%Y-%m-%d 00:00:00")
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) as cnt FROM shorts WHERE status = 'uploaded' AND created_at >= ?",
            (cutoff,),
        )
        return cursor.fetchone()["cnt"]


# Initialize on import
init_db()
