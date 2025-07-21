import threading
import time
from datetime import datetime
import requests
from src.config import APIConfig, logger

TOKENS_PRINCIPALES = [
    "bitcoin", "ethereum", "solana", "cardano", "ripple",
    "dogecoin", "binancecoin", "matic-network", "polkadot", "litecoin"
]

_precio_cache = {}

def get_precio_desde_cache(token_id: str) -> dict:
    """Devuelve el precio en caché si está disponible"""
    token_id = token_id.lower()
    if token_id in _precio_cache:
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
