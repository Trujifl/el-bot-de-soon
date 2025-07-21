import requests
import time
from datetime import datetime, timedelta
from src.config import APIConfig, logger
from src.services.crypto_mapper import crypto_mapper

class CoinGeckoAPI:
    _BASE_DELAY = 12  
    _MAX_DELAY = 60
    _last_call_time = 0
    _current_delay = _BASE_DELAY

    _PRICE_CACHE = {}
    _PRICE_CACHE_TTL = timedelta(minutes=5)

    @classmethod
    def _enforce_rate_limit(cls):
        """Aplica delay para evitar ser bloqueado por CoinGecko"""
        elapsed = time.time() - cls._last_call_time
        if elapsed < cls._current_delay:
            time.sleep(cls._current_delay - elapsed)
        cls._last_call_time = time.time()

    @classmethod
    def obtener_precio(cls, consulta: str) -> dict:
        """Obtiene el precio de una criptomoneda desde CoinGecko con caché y control de límites"""
        try:
            cache_key = consulta.lower()
            if cache_key in cls._PRICE_CACHE:
                data, timestamp = cls._PRICE_CACHE[cache_key]
                if datetime.now() - timestamp < cls._PRICE_CACHE_TTL:
                    return data

            cripto_id = crypto_mapper.find_coin(consulta)
            if not cripto_id:
                raise ValueError(f"No se pudo reconocer la cripto '{consulta}'")

            cls._enforce_rate_limit()

            price_url = (
                f"{APIConfig.COINGECKO_URL}/simple/price?"
                f"ids={cripto_id}&vs_currencies=usd&include_24hr_change=true"
            )
            price_response = requests.get(
                price_url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            price_response.raise_for_status()
            price_data = price_response.json()

            if cripto_id not in price_data:
                raise ValueError("Datos de precio no recibidos")

            resultado = {
                "nombre": cripto_id.replace("-", " ").title(),
                "simbolo": consulta.upper(),
                "precio": float(price_data[cripto_id]["usd"]),
                "cambio_24h": float(price_data[cripto_id].get("usd_24h_change", 0)),
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            cls._PRICE_CACHE[cache_key] = (resultado, datetime.now())
            cls._current_delay = max(cls._BASE_DELAY, cls._current_delay * 0.9)

            return resultado

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                cls._current_delay = min(cls._MAX_DELAY, cls._current_delay * 2)
                logger.warning(f"Rate limit alcanzado. Delay aumentado a {cls._current_delay}s")
            raise ValueError(f"Error de API: {str(e)}")

        except Exception as e:
            logger.error(f"Error al procesar '{consulta}': {str(e)}")
            raise ValueError(f"No se pudo obtener precio para '{consulta}'")
