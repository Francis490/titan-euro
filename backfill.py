"""Modulo di Backfill per popolare il database con lo storico."""

import logging
from datetime import datetime
from database import upsert_draw, init_db, count_draws
from models import EurojackpotDraw

logger = logging.getLogger(__name__)

# Storico di test (in futuro questo verrà scaricato da un file CSV o API)
MOCK_HISTORY = [
    {"date": "2026-10-24", "main": [5, 12, 23, 34, 45], "euro": [3, 7]},
    {"date": "2026-10-20", "main": [2, 15, 28, 39, 49], "euro": [1, 10]},
    {"date": "2026-10-17", "main": [8, 19, 22, 40, 50], "euro": [5, 12]},
]

def run_backfill():
    logger.info("Avvio Backfill storico...")
    init_db()
    
    success_count = 0
    for item in MOCK_HISTORY:
        try:
            # Creiamo il modello Pydantic (che valida i dati)
            draw = EurojackpotDraw(
                draw_date=datetime.strptime(item["date"], "%Y-%m-%d").date(),
                main_numbers=item["main"],
                euro_numbers=item["euro"],
                source="backfill_mock"
            )
            # Inseriamo nel DB (in modo idempotente)
            if upsert_draw(draw):
                success_count += 1
        except Exception as e:
            logger.error(f"Errore scartando estrazione {item['date']}: {e}")
            
    total = count_draws()
    logger.info(f"Backfill completato: {success_count} nuove estrazioni inserite.")
    logger.info(f"Totale estrazioni attuali nel DB: {total}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_backfill()
