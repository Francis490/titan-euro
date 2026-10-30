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
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS draws (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date       TEXT    NOT NULL UNIQUE,
    num_1           INTEGER NOT NULL CHECK (num_1 BETWEEN 1 AND 50),
    num_2           INTEGER NOT NULL CHECK (num_2 BETWEEN 1 AND 50),
    num_3           INTEGER NOT NULL CHECK (num_3 BETWEEN 1 AND 50),
    num_4           INTEGER NOT NULL CHECK (num_4 BETWEEN 1 AND 50),
    num_5           INTEGER NOT NULL CHECK (num_5 BETWEEN 1 AND 50),
    euro_1          INTEGER NOT NULL CHECK (euro_1 BETWEEN 1 AND 12),
    euro_2          INTEGER NOT NULL CHECK (euro_2 BETWEEN 1 AND 12),
    source          TEXT    NOT NULL DEFAULT 'multipasko.pl',
    fetched_at      TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_draws_date ON draws(draw_date DESC);
"""

@contextmanager
def get_connection(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager per connessioni SQLite sicure."""
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
    """Crea schema e indici se non esistono. Idempotente."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
    logger.info("Database inizializzato (schema pronto)")

def upsert_draw(draw: EurojackpotDraw, db_path: Optional[Path] = None) -> bool:
    """Inserisce un'estrazione in modo idempotente."""
    sql = """
    INSERT INTO draws (draw_date, num_1, num_2, num_3, num_4, num_5,
                       euro_1, euro_2, source, fetched_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(draw_date) DO NOTHING;
    """
    params = (
        draw.draw_date.isoformat(),
        *draw.main_numbers,
        *draw.euro_numbers,
        draw.source,
        draw.fetched_at.isoformat(timespec="seconds"),
    )
    with get_connection(db_path) as conn:
        cur = conn.execute(sql, params)
        inserted = cur.rowcount > 0
    if inserted:
        logger.info("Inserita estrazione del %s", draw.draw_date.isoformat())
    else:
        logger.debug("Estrazione del %s già presente, skip", draw.draw_date.isoformat())
    return inserted

def get_latest_draw_date(db_path: Optional[Path] = None) -> Optional[date]:
    """Restituisce la data dell'ultima estrazione salvata, o None."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT draw_date FROM draws ORDER BY draw_date DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    return date.fromisoformat(row["draw_date"])

def count_draws(db_path: Optional[Path] = None) -> int:
    """Numero di estrazioni salvate (utile per smoke test)."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM draws").fetchone()
    return int(row["n"])
