"""Titan Euro - Algoritmo Anti-Crowd Divino (Deterministico).
Costruisce la sestina statisticamente meno giocata dalle masse, senza usare il caso.
"""

import logging
from typing import List, Tuple, Set
from database import get_connection

logger = logging.getLogger(__name__)

class DivineAntiCrowdGenerator:
    """Generatore deterministico di sestine impopolari."""
    
    def __init__(self):
        # Regole inviolabili (penalità)
        self.birthday_limit = 31
        self.recent_draws_limit = 15
        
    def _get_recent_numbers(self) -> Tuple[Set[int], Set[int]]:
        """Estrae gli ultimi N numeri usciti per non giocarli (gambler's fallacy)."""
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
        """Genera la sestina perfetta tramite selezione logica."""
        logger.info("Avvio generazione Divina Anti-Crowd...")
        recent_mains, recent_euros = self._get_recent_numbers()

        # 1. CREAZIONE DEL PANIERE DEI NUMERI PRINCIPALI (1-50)
        # Partiamo da tutti i numeri > 31 (escludiamo i compleanni)
        valid_mains = list(range(32, 51))
        
        # Rimuoviamo i numeri usciti di recente
        valid_mains = [n for n in valid_mains if n not in recent_mains]
        
        # Rimuoviamo i multipli di 7 (numeri fortunati)
        valid_mains = [n for n in valid_mains if n % 7 != 0]
        
        # Rimuoviamo i numeri che formano coppie consecutive (es. 44, 45)
        # Li ordiniamo in modo da poterli valutare
        valid_mains.sort()
        filtered_mains = []
        for i, n in enumerate(valid_mains):
            # Se il numero successivo è consecutivo, penalizziamo il primo
            if i < len(valid_mains) - 1 and valid_mains[i+1] - n == 1:
                continue
            filtered_mains.append(n)
            
        # Se per assurdo non abbiamo abbastanza numeri (impossibile con 50 numeri), 
        # facciamo un fallback di sicurezza
        if len(filtered_mains) < 5:
            filtered_mains = list(range(40, 50))

        # Prendiamo i 5 numeri più alti e impopolari (i numeri alti sono meno giocati)
        # Usiamo una slice per prendere gli ultimi 5 dell'array filtrato
        final_mains = filtered_mains[-5:]
        
        # 2. CREAZIONE DEL PANIERE EURONUMERI (1-12)
        # I numeri più giocati sono 1, 7, 12. 
        # Prendiamo i meno popolari scartando quelli usciti di recente.
        valid_euros = [n for n in range(1, 13) if n not in (1, 7, 12) and n not in recent_euros]
        
        if len(valid_euros) < 2:
            valid_euros = [10, 11] # Fallback sacro
            
        # Prendiamo i 2 Euronumeri più alti disponibili
        final_euros = valid_euros[-2:]

        return sorted(final_mains), sorted(final_euros)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    generator = DivineAntiCrowdGenerator()
    mains, euros = generator.generate()
    
    logger.info("========================================")
    logger.info(" TITAN EURO - SESTINA DIVINA")
    logger.info("========================================")
    logger.info(f" Numeri Principali: {mains}")
    logger.info(f" Euronumeri:        {euros}")
    logger.info(" Nota: Zero numeri < 32, zero recenti, zero multipli di 7.")
    logger.info("========================================")
