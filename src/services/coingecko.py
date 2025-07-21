import requests
import time
from datetime import datetime
from src.config import APIConfig, logger

class CoinGeckoAPI:
    # Control de rate limits
    _last_request_time = 0
    REQUEST_DELAY = 7  # 7 segundos entre llamadas (~8/min)
    CACHE = {}
    CACHE_TTL = 300  # 5 minutos

    @classmethod
    def obtener_precio(cls, cripto_id: str) -> dict:
        """Obtiene precio con caché y control de rate limits."""
        cripto_id = cripto_id.lower()
        
        # Verificar caché primero
        if cripto_id in cls.CACHE:
            cached_data, timestamp = cls.CACHE[cripto_id]
            if (datetime.now() - timestamp).total_seconds() < cls.CACHE_TTL:
                logger.info(f"Devolviendo datos en caché para {cripto_id}")
                return cached_data

        # Control de rate limit
        cls._enforce_rate_limit()

        try:
            # Primera llamada para precio y cambio
            price_url = f"{APIConfig.COINGECKO_URL}/simple/price?ids={cripto_id}&vs_currencies=usd&include_24hr_change=true"
            price_data = cls._make_api_call(price_url)
            
            if cripto_id not in price_data or "usd" not in price_data[cripto_id]:
                raise ValueError("Estructura de precio inválida")

            # Segunda llamada para metadatos
            detail_url = f"{APIConfig.COINGECKO_URL}/coins/{cripto_id}"
            detail_data = cls._make_api_call(detail_url)

            # Validación de datos
            required_fields = ["name", "symbol", "market_data"]
            if not all(field in detail_data for field in required_fields):
                raise ValueError("Faltan campos esenciales")

            # Construir respuesta
            result = {
                "nombre": detail_data["name"],
                "simbolo": detail_data["symbol"].upper(),
                "precio": float(price_data[cripto_id]["usd"]),
                "cambio_24h": float(price_data[cripto_id].get("usd_24h_change", 0)),
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            # Actualizar caché
            cls.CACHE[cripto_id] = (result, datetime.now())
            return result

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                cls.REQUEST_DELAY = min(60, cls.REQUEST_DELAY * 2)  # Backoff exponencial
                logger.warning(f"Rate limit alcanzado. Nuevo delay: {cls.REQUEST_DELAY}s")
            raise

    @classmethod
    def _enforce_rate_limit(cls):
        """Garantiza el tiempo entre solicitudes."""
        elapsed = time.time() - cls._last_request_time
        if elapsed < cls.REQUEST_DELAY:
            wait_time = cls.REQUEST_DELAY - elapsed
            time.sleep(wait_time)
        cls._last_request_time = time.time()

    @classmethod
    def _make_api_call(cls, url: str):
        """Método centralizado para llamadas API."""
        cls._enforce_rate_limit()
        response = requests.get(
            url,
            timeout=APIConfig.COINGECKO_TIMEOUT,
            headers=APIConfig.REQUEST_HEADERS
        )
        response.raise_for_status()
        return response.json()
