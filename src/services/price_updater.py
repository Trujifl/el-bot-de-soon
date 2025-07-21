# src/services/price_updater.py

import threading
import time
from datetime import datetime
import requests
from src.config import APIConfig, logger

TOKEN_ALIASES = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "sol": "solana",
    "solana": "solana",
    "ada": "cardano",
    "cardano": "cardano",
    "xrp": "ripple",
    "ripple": "ripple",
    "doge": "dogecoin",
    "dogecoin": "dogecoin",
    "bnb": "binancecoin",
    "binance": "binancecoin",
    "matic": "matic-network",
    "polygon": "matic-network",
    "dot": "polkadot",
    "polkadot": "polkadot",
    "ltc": "litecoin",
    "litecoin": "litecoin",
}

TOKENS_PRINCIPALES = list(set(TOKEN_ALIASES.values()))

_precio_cache = {}

def normalizar_token_id(user_input: str) -> str:
    """Devuelve el ID oficial del token según alias."""
    return TOKEN_ALIASES.get(user_input.lower())

def get_precio_desde_cache(token_input: str) -> dict:
    """Devuelve el precio en caché si está disponible"""
    token_id = normalizar_token_id(token_input)
    if token_id and token_id in _precio_cache:
        return _precio_cache[token_id]
    return None

def actualizar_precios():
    """Consulta periódicamente CoinGecko para los tokens principales"""
    while True:
        try:
            ids_str = ",".join(TOKENS_PRINCIPALES)
            url = f"{APIConfig.COINGECKO_URL}/simple/price?ids={ids_str}&vs_currencies=usd&include_24hr_change=true"
            response = requests.get(
                url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            response.raise_for_status()
            data = response.json()
            now = datetime.now().strftime("%d/%m/%Y %H:%M")

            for token_id in TOKENS_PRINCIPALES:
                if token_id in data:
                    _precio_cache[token_id] = {
                        "nombre": token_id.replace("-", " ").title(),
                        "simbolo": token_id[:4].upper(),
                        "precio": float(data[token_id]["usd"]),
                        "cambio_24h": float(data[token_id].get("usd_24h_change", 0)),
                        "ultima_actualizacion": now
                    }
            logger.info("✅ Precios actualizados desde CoinGecko")

        except Exception as e:
            logger.error(f"❌ Error actualizando precios desde CoinGecko: {e}")

        time.sleep(60)

def iniciar_actualizador():
    thread = threading.Thread(target=actualizar_precios, daemon=True)
    thread.start()

