"""Modulo per l'invio della sestina su Telegram."""

import os
import logging
import requests
from anti_crowd import DivineAntiCrowdGenerator

logger = logging.getLogger(__name__)

def send_telegram_message():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("Credenziali Telegram mancanti nei Secrets di GitHub.")
        return

    # Genera la sestina usando l'algoritmo deterministico
    generator = DivineAntiCrowdGenerator()
    mains, euros = generator.generate()

    # Formattiamo il messaggio con Markdown
    message = (
        "🎯 *TITAN EURO - SESTINA DIVINA* 🎯\n\n"
        f"🔢 *Numeri Principali:*\n`{', '.join(map(str, mains))}`\n\n"
        f"⭐ *Euronumeri:*\n`{', '.join(map(str, euros))}`\n\n"
        "🛡️ _Zero numeri < 32, zero recenti, zero caos._\n"
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
