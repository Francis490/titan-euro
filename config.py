"""Configurazione centralizzata di Titan Euro — FASE 1."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "titan_euro.db"

FETCH_TIMEOUT_SECONDS = 15
FETCH_MAX_RETRIES = 3
FETCH_BACKOFF_BASE = 1.5

PRIMARY_SOURCE_URL = "https://www.multipasko.pl/widget-wyniki.php?format=json"

LOG_LEVEL = os.getenv("TITAN_EURO_LOG_LEVEL", "INFO")
