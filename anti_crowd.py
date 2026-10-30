"""Titan Euro - Algoritmo Anti-Crowd Divino."""

import logging
import json
from pathlib import Path
from typing import List, Tuple, Set
from database import get_connection

logger = logging.getLogger(__name__)

class DivineAntiCrowdGenerator:
    def __init__(self):
        self.birthday_limit = 31
        # Fissiamo il limite a 5 estrazioni recenti, altrimenti svuotiamo il paniere
        self.recent_draws_limit = 5
        
    def _get_recent_numbers(self) -> Tuple[Set[int], Set[int]]:
        recent_mains, recent_euros = set(), set()
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT num_1, num_2, num_3, num_4, num_5, euro_1, euro_2 FROM draws ORDER BY draw_date DESC LIMIT ?", 
                (self.recent_draws_limit,)
            ).fetchall()
            for row in rows:
                recent_mains.update([row["num_1"], row["num_2"], row["num_3"], row["num_4"], row["num_5"]])
                recent_euros.update([row["euro_1"], row["euro_2"]])
        return recent_mains, recent_euros

    def generate(self) -> Tuple[List[int], List[int]]:
        recent_mains, recent_euros = self._get_recent_numbers()
        
        # 1. Partiamo dai numeri alti (escludendo i compleanni)
        valid_mains = list(range(32, 51))
        
        # 2. Escludiamo i numeri usciti nelle ultime 5 estrazioni
        valid_mains = [n for n in valid_mains if n not in recent_mains]
        
        # 3. Escludiamo i multipli di 7 (i numeri portafortuna)
        valid_mains = [n for n in valid_mains if n % 7 != 0]
        
        # Fallback di sicurezza: se abbiamo meno di 5 numeri, ignoriamo i recenti
        if len(valid_mains) < 5:
            valid_mains = [n for n in range(32, 51) if n % 7 != 0]

        # 4. Ordiniamo e selezioniamo a mano per evitare numeri consecutivi (es. 44, 45)
        valid_mains.sort()
        final_mains = []
        for n in valid_mains:
            # Se l'ultimo numero scelto è consecutivo a questo, lo saltiamo
            if final_mains and n - final_mains[-1] <= 1:
                continue
            final_mains.append(n)
            if len(final_mains) == 5:
                break
                
        # Se per assurdo non abbiamo ancora 5 numeri, prendiamo gli ultimi disponibili
        if len(final_mains) < 5:
            final_mains = valid_mains[-5:]

        # EURONUMERI (1-12)
        valid_euros = [n for n in range(1, 13) if n not in (1, 7, 12) and n not in recent_euros]
        if len(valid_euros) < 2:
            valid_euros = [10, 11]
        final_euros = valid_euros[-2:]

        return sorted(final_mains), sorted(final_euros)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generator = DivineAntiCrowdGenerator()
    mains, euros = generator.generate()
    
    # Salva per la PWA
    data = {
        "main_numbers": mains,
        "euro_numbers": euros,
        "timestamp": "Ultima generazione"
    }
    
    Path("docs").mkdir(exist_ok=True)
    with open("docs/latest.json", "w") as f:
        json.dump(data, f, indent=4)
        
    logger.info(f"Sestina generata e salvata: {mains} + {euros}")
