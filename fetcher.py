"""Fetcher blindato per le estrazioni Eurojackpot."""

import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional
import requests
from pydantic import ValidationError
from config import FETCH_BACKOFF_BASE, FETCH_MAX_RETRIES, FETCH_TIMEOUT_SECONDS, PRIMARY_SOURCE_URL
from database import get_latest_draw_date, upsert_draw
from models import EurojackpotDraw

logger = logging.getLogger(__name__)

class FetchError(Exception):
    pass

def _request_with_retries(url: str) -> Dict[str, Any]:
    last_exc = None
    for attempt in range(1, FETCH_MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=FETCH_TIMEOUT_SECONDS, headers={"User-Agent": "TitanEuro/1.0"})
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as exc:
            if exc.response is not None and 400 <= exc.response.status_code < 500:
                raise FetchError("Errore HTTP client") from exc
            last_exc = exc
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exc = exc
        except ValueError as exc:
            raise FetchError("JSON non valido") from exc
        if attempt < FETCH_MAX_RETRIES:
            time.sleep(FETCH_BACKOFF_BASE ** attempt)
    raise FetchError("Fetch fallito") from last_exc

def _parse_multipasko_eurojackpot(payload: Dict[str, Any]) -> EurojackpotDraw:
    ej = payload.get("g", {}).get("eurojackpot", {})
    date_raw, main_raw, euro_raw = ej.get("d"), ej.get("l"), ej.get("x")
    if not isinstance(main_raw, list) or not isinstance(euro_raw, list):
        raise FetchError("Numeri mancanti")
    draw_date = datetime.strptime(date_raw.strip(), "%d.%m.%Y").date()
    return EurojackpotDraw(draw_date=draw_date, main_numbers=main_raw, euro_numbers=euro_raw)

def fetch_and_store_latest(db_path=None) -> bool:
    try:
        payload = _request_with_retries(PRIMARY_SOURCE_URL)
        draw = _parse_multipasko_eurojackpot(payload)
    except Exception as exc:
        logger.error(f"Fetch fallito: {exc}")
        return False
    latest = get_latest_draw_date(db_path)
    if latest is not None and draw.draw_date <= latest:
        return False
    return upsert_draw(draw, db_path)
