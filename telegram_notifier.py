"""Modulo per l'invio della sestina su Telegram usando il Jackpot Hunter."""

import os
import logging
import requests
import json
from pathlib import Path
from jackpot_hunter import get_hunter_numbers

logger = logging.getLogger(__name__)

def send_telegram_message():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("Credenziali Telegram mancanti.")
        return

    # Genera la sestina usando il Jackpot Hunter
    mains, euros = get_hunter_numbers()

    # Salva per la PWA (Dashboard)
    data = {
        "main_numbers": mains,
        "euro_numbers": euros,
        "timestamp": "Ultima generazione (Hunter)"
    }
    Path("docs").mkdir(exist_ok=True)
    with open("docs/latest.json", "w") as f:
        json.dump(data, f, indent=4)

    # Formattiamo il messaggio con Markdown
    message = (
        "🎯 *TITAN EURO - JACKPOT HUNTER* 🎯\n\n"
        f"🔢 *Numeri Principali:*\n`{', '.join(map(str, mains))}`\n\n"
        f"⭐ *Euronumeri:*\n`{', '.join(map(str, euros))}`\n\n"
        "📊 _Algoritmo basato su Bias di Frequenza e Ritardo._\n"
        "🍀 _In bocca al lupo!_"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Messaggio Telegram inviato con successo!")
    except Exception as e:
        logger.error(f"Errore nell'invio del messaggio Telegram: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    send_telegram_message()
