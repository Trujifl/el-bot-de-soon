import requests
import time
from datetime import datetime, timedelta
from src.config import APIConfig, logger
from src.services.crypto_mapper import crypto_mapper
from src.services.price_updater import get_precio_desde_cache

class CoinGeckoAPI:
    _BASE_DELAY = 12  
    _MAX_DELAY = 60
    _last_call_time = 0
    _current_delay = _BASE_DELAY

    _PRICE_CACHE = {}
    _PRICE_CACHE_TTL = timedelta(minutes=5)

    @classmethod
    def _enforce_rate_limit(cls):
        elapsed = time.time() - cls._last_call_time
        if elapsed < cls._current_delay:
            time.sleep(cls._current_delay - elapsed)
        cls._last_call_time = time.time()

    @classmethod
    def obtener_precio(cls, consulta: str) -> dict:
        # ✅ Primero intentamos usar el caché compartido de price_updater
        datos = get_precio_desde_cache(consulta)
        if datos:
            return datos

        cache_key = consulta.lower()

        # Luego el caché privado de esta clase
        if cache_key in cls._PRICE_CACHE:
            data, timestamp = cls._PRICE_CACHE[cache_key]
            if datetime.now() - timestamp < cls._PRICE_CACHE_TTL:
                return data

        cripto_id = crypto_mapper.find_coin(consulta)
        if not cripto_id:
            raise ValueError(f"No se pudo reconocer la cripto '{consulta}'")

        def fetch_price():
            cls._enforce_rate_limit()
            price_url = (
                f"{APIConfig.COINGECKO_URL}/simple/price?"
                f"ids={cripto_id}&vs_currencies=usd&include_24hr_change=true"
            )
            response = requests.get(
                price_url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            response.raise_for_status()
            return response.json()

        try:
            price_data = fetch_price()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                cls._current_delay = min(cls._MAX_DELAY, cls._current_delay * 2)
                logger.warning(f"Rate limit alcanzado. Delay aumentado a {cls._current_delay}s")
                time.sleep(cls._current_delay)
                try:
                    price_data = fetch_price()
                except Exception as retry_error:
                    if cache_key in cls._PRICE_CACHE:
                        logger.warning("Usando precio en caché tras fallo 429")
                        return cls._PRICE_CACHE[cache_key][0]
                    raise ValueError("CoinGecko está limitando consultas. Intenta más tarde.")
            else:
                raise ValueError(f"Error de API: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            raise ValueError("No se pudo obtener el precio actual.")

        if cripto_id not in price_data:
            raise ValueError("CoinGecko no devolvió datos para esta cripto.")

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

