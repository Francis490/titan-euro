import csv
import logging
import json
from pathlib import Path
from collections import Counter

logger = logging.getLogger(__name__)

def get_hunter_numbers(file_path="EJ_ab_2022.csv"):
    main_counter = Counter()
    euro_counter = Counter()
    total_draws = 0
    all_mains_history = []
    all_euros_history = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f, delimiter=';')
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

        if total_draws == 0: return [1,2,3,4,5], [1,2]

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

        main_scores = {n: (main_counter.get(n, 0) / avg_main) + (main_gaps[n] / 10.0) for n in range(1, 51)}
        euro_scores = {n: (euro_counter.get(n, 0) / avg_euro) + (euro_gaps[n] / 10.0) for n in range(1, 13)}

        top_mains = sorted(main_scores.keys(), key=lambda x: main_scores[x], reverse=True)[:5]
        top_euros = sorted(euro_scores.keys(), key=lambda x: euro_scores[x], reverse=True)[:2]

        return sorted(top_mains), sorted(top_euros)

    except FileNotFoundError:
        return [1,2,3,4,5], [1,2]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    mains, euros = get_hunter_numbers()
    logger.info(f" SESTINA JACKPOT HUNTER: {mains} + {euros}")
