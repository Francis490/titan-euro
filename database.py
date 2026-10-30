"""Gestione del database SQLite di Titan Euro."""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Generator, Optional
from models import EurojackpotDraw

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date TEXT NOT NULL UNIQUE,
    num_1 INTEGER NOT NULL CHECK (num_1 BETWEEN 1 AND 50),
    num_2 INTEGER NOT NULL CHECK (num_2 BETWEEN 1 AND 50),
    num_3 INTEGER NOT NULL CHECK (num_3 BETWEEN 1 AND 50),
    num_4 INTEGER NOT NULL CHECK (num_4 BETWEEN 1 AND 50),
    num_5 INTEGER NOT NULL CHECK (num_5 BETWEEN 1 AND 50),
    euro_1 INTEGER NOT NULL CHECK (euro_1 BETWEEN 1 AND 10),
    euro_2 INTEGER NOT NULL CHECK (euro_2 BETWEEN 1 AND 10),
    source TEXT NOT NULL DEFAULT 'multipasko.pl',
    fetched_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_draws_date ON draws(draw_date DESC);
"""

@contextmanager
def get_connection(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    from config import DB_PATH
    path = db_path or DB_PATH
    conn = sqlite3.connect(str(path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path: Optional[Path] = None) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)

def upsert_draw(draw: EurojackpotDraw, db_path: Optional[Path] = None) -> bool:
    sql = "INSERT INTO draws (draw_date, num_1, num_2, num_3, num_4, num_5, euro_1, euro_2, source, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(draw_date) DO NOTHING;"
    params = (draw.draw_date.isoformat(), *draw.main_numbers, *draw.euro_numbers, draw.source, draw.fetched_at.isoformat(timespec="seconds"))
    with get_connection(db_path) as conn:
        cur = conn.execute(sql, params)
        return cur.rowcount > 0

def count_draws(db_path: Optional[Path] = None) -> int:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM draws").fetchone()
    return int(row["n"])
