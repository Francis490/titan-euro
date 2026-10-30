"""Entry point per eseguire la FASE 1: init DB + fetch + report."""

import logging
import sys
from config import LOG_LEVEL
from database import count_draws, init_db
from fetcher import fetch_and_store_latest

def main() -> int:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    init_db()
    inserted = fetch_and_store_latest()
    total = count_draws()
    print(f"Risultato: inserted={inserted} | totale in DB={total}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
