import requests
import time
from datetime import datetime
from src.config import APIConfig, logger

class CoinGeckoAPI:
    # Variables de clase para control de rate limit
    _last_call_time = 0
    _current_delay = 7  # Empezamos con 7 segundos (8-9 requests/min)
    _max_delay = 60  # Máximo 60 segundos de delay
    _cache = {}
    _cache_ttl = 180  # Cache de 3 minutos

    @classmethod
    def obtener_precio(cls, cripto_id: str) -> dict:
        """Versión optimizada con gestión inteligente de rate limits"""
        cripto_id = cripto_id.lower()
        
        # 1. Primero verificar caché
        cached_data = cls._check_cache(cripto_id)
        if cached_data:
            return cached_data

        # 2. Control de rate limit
        cls._wait_for_next_call()

        try:
            # 3. Llamada a la API
            url = f"{APIConfig.COINGECKO_URL}/simple/price?ids={cripto_id}&vs_currencies=usd&include_24hr_change=true"
            response = cls._make_request(url)
            price_data = response.json()

            # 4. Validación básica
            if not price_data.get(cripto_id):
                raise ValueError("Datos de precio no recibidos")

            # 5. Procesamiento (igual que antes)
            precio = float(price_data[cripto_id]["usd"])
            cambio_24h = float(price_data[cripto_id].get("usd_24h_change", 0))
            
            # 6. Armado de respuesta (sin cambios)
            resultado = {
                "nombre": cripto_id.capitalize(),
                "simbolo": cripto_id.upper()[:3],
                "precio": precio,
                "cambio_24h": cambio_24h,
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            # 7. Actualizar caché
            cls._cache[cripto_id] = (resultado, datetime.now())
            cls._reduce_delay()  # Intentamos acelerar si hay éxito
            return resultado

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                cls._increase_delay()
                logger.warning(f"Rate limit alcanzado. Nuevo delay: {cls._current_delay}s")
            raise ValueError(f"Error de API: {e}") from e

    # --- Métodos auxiliares (nuevos) ---
    @classmethod
    def _check_cache(cls, cripto_id: str):
        """Verifica si hay datos válidos en caché"""
        if cripto_id in cls._cache:
            data, timestamp = cls._cache[cripto_id]
            if (datetime.now() - timestamp).total_seconds() < cls._cache_ttl:
                logger.info(f"Usando caché para {cripto_id}")
                return data
        return None

    @classmethod
    def _wait_for_next_call(cls):
        """Espera el tiempo necesario entre llamadas"""
        elapsed = time.time() - cls._last_call_time
        if elapsed < cls._current_delay:
            wait_time = cls._current_delay - elapsed
            time.sleep(wait_time)
        cls._last_call_time = time.time()

    @classmethod
    def _make_request(cls, url: str):
        """Método centralizado para requests con timeout"""
        try:
            response = requests.get(
                url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            raise ValueError("Timeout al conectar con CoinGecko")

    @classmethod
    def _increase_delay(cls):
        """Aumenta el delay exponencialmente (hasta _max_delay)"""
        cls._current_delay = min(cls._current_delay * 2, cls._max_delay)

    @classmethod
    def _reduce_delay(cls):
        """Reduce el delay gradualmente cuando todo va bien"""
        cls._current_delay = max(7, cls._current_delay * 0.9)  # Reduce 10%
