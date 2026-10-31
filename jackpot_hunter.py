import csv
import logging
from collections import Counter

logger = logging.getLogger(__name__)

def hunt_jackpot(file_path="EJ_ab_2022.csv"):
    logger.info("=== AVVIO JACKPOT HUNTER: CACCIA AL 5+2 ===")
    main_counter = Counter()
    euro_counter = Counter()
    total_draws = 0
    
    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f, delimiter=';')
            all_mains_history = []
            all_euros_history = []
            
            for row in reader:
                if len(row) < 8 or not row[0].strip() or row[0].strip() == "Datum":
                    continue
                try:
                    mains = [int(row[i].strip()) for i in range(1, 6)]
                    euros = [int(row[i].strip()) for i in range(6, 8)]
                    main_counter.update(mains)
                    euro_counter.update(euros)
                    all_mains_history.append(mains)
                    all_euros_history.append(euros)
                    total_draws += 1
                except ValueError:
                    continue

        if total_draws == 0:
            logger.error("Dati non validi.")
            return

        main_gaps = {n: 0 for n in range(1, 51)}
        euro_gaps = {n: 0 for n in range(1, 13)}
        
        for i, draw in enumerate(reversed(all_mains_history)):
            for n in range(1, 51):
                if n in draw:
                    if main_gaps[n] == 0: main_gaps[n] = i
                else:
                    if main_gaps[n] == 0: main_gaps[n] = i
                         
        for i, draw in enumerate(reversed(all_euros_history)):
            for n in range(1, 13):
                if n in draw:
                    if euro_gaps[n] == 0: euro_gaps[n] = i
                else:
                    if euro_gaps[n] == 0: euro_gaps[n] = i

        avg_main = (total_draws * 5) / 50
        avg_euro = (total_draws * 2) / 12

        main_scores = {}
        for n in range(1, 51):
            freq = main_counter.get(n, 0)
            gap = main_gaps[n]
            score = (freq / avg_main) + (gap / 10.0)
            main_scores[n] = score

        euro_scores = {}
        for n in range(1, 13):
            freq = euro_counter.get(n, 0)
            gap = euro_gaps[n]
            score = (freq / avg_euro) + (gap / 10.0)
            euro_scores[n] = score

        top_mains = sorted(main_scores.keys(), key=lambda x: main_scores[x], reverse=True)[:5]
        top_euros = sorted(euro_scores.keys(), key=lambda x: euro_scores[x], reverse=True)[:2]

        logger.info("========================================")
        logger.info(" SESTINA JACKPOT HUNTER (5+2) ")
        logger.info("========================================")
        logger.info(f" SESTINA DA GIOCARE: {sorted(top_mains)} + {sorted(top_euros)}")
        logger.info("========================================")

    except FileNotFoundError:
        logger.error("File CSV non trovato.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    hunt_jackpot()
