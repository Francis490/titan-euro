"""Backfill massivo da file CSV locale."""

import csv
import logging
from datetime import datetime
from database import init_db, upsert_draw, count_draws
from models import EurojackpotDraw

logger = logging.getLogger(__name__)

def run_csv_backfill(file_path="EJ_ab_2022.csv"):
    logger.info(f"Avvio Backfill massivo da {file_path}...")
    init_db()
    
    success = 0
    errors = 0
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            # Il tuo CSV usa il punto e virgola come separatore
            reader = csv.reader(f, delimiter=';')
            
            for row in reader:
                # Salta l'intestazione, le righe vuote o i piè di pagina
                if len(row) < 8 or not row[0].strip() or row[0].strip() == "Datum":
                    continue
                    
                try:
                    # 1. Data (DD.MM.YYYY)
                    date_str = row[0].strip()
                    draw_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                    
                    # 2. Numeri Principali (colonne 1-5)
                    mains = [int(row[i].strip()) for i in range(1, 6)]
                    
                    # 3. Euronumeri (colonne 6-7)
                    euros = [int(row[i].strip()) for i in range(6, 8)]
                    
                    # 4. Validazione Pydantic e Inserimento
                    draw = EurojackpotDraw(
                        draw_date=draw_date,
                        main_numbers=mains,
                        euro_numbers=euros,
                        source="csv_backfill"
                    )
                    
                    if upsert_draw(draw):
                        success += 1
                        
                except Exception as e:
                    # Se una riga è corrotta, la saltiamo e logghiamo l'errore senza far crashare il bot
                    logger.warning(f"Riga scartata ({row[0]}): {e}")
                    errors += 1
                    
        logger.info(f"Backfill completato! Inserite: {success} | Scartate: {errors}")
        logger.info(f"Totale estrazioni nel DB: {count_draws()}")

    except FileNotFoundError:
        logger.error(f"File {file_path} non trovato! Assicurati di averlo caricato su GitHub.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_csv_backfill()
