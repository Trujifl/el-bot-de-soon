import requests
import time
from datetime import datetime, timedelta
from src.config import APIConfig, logger

class CoinGeckoAPI:
    # Configuración de rate limiting
    _BASE_DELAY = 12  # 12 segundos entre llamadas (5/min)
    _MAX_DELAY = 60  # Máximo 60 segundos
    _last_call_time = 0
    _current_delay = _BASE_DELAY
    
    # Cache para datos
    _CRYPTO_LIST_CACHE = None
    _CRYPTO_LIST_LAST_UPDATE = None
    _CRYPTO_LIST_TTL = timedelta(hours=24)  # Actualizar lista cada 24h
    _PRICE_CACHE = {}
    _PRICE_CACHE_TTL = timedelta(minutes=5)  # Cache de precios por 5 min

    @classmethod
    def _enforce_rate_limit(cls):
        """Control estricto del rate limiting"""
        elapsed = time.time() - cls._last_call_time
        if elapsed < cls._current_delay:
            time.sleep(cls._current_delay - elapsed)
        cls._last_call_time = time.time()

    @classmethod
    def _get_crypto_list(cls):
        """Obtiene la lista de criptomonedas con cache"""
        if cls._CRYPTO_LIST_CACHE and (datetime.now() - cls._CRYPTO_LIST_LAST_UPDATE < cls._CRYPTO_LIST_TTL):
            return cls._CRYPTO_LIST_CACHE

        cls._enforce_rate_limit()
        try:
            response = requests.get(
                f"{APIConfig.COINGECKO_URL}/coins/list",
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            response.raise_for_status()
            cls._CRYPTO_LIST_CACHE = response.json()
            cls._CRYPTO_LIST_LAST_UPDATE = datetime.now()
            return cls._CRYPTO_LIST_CACHE
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                cls._current_delay = min(cls._MAX_DELAY, cls._current_delay * 2)
                logger.warning(f"Rate limit alcanzado. Nuevo delay: {cls._current_delay}s")
            raise

    @classmethod
    def _get_crypto_id(cls, query: str):
        """Encuentra el ID de criptomoneda más cercano"""
        cryptos = cls._get_crypto_list()
        query = query.lower().strip()
        
        # Primero busca coincidencia exacta
        for crypto in cryptos:
            if (query == crypto['id'].lower() or 
                query == crypto['symbol'].lower() or 
                query == crypto['name'].lower()):
                return crypto['id']
        
        # Luego busca aproximada
        for crypto in cryptos:
            if (query in crypto['id'].lower() or 
                query in crypto['name'].lower()):
                return crypto['id']
        
        raise ValueError(f"Cripto no encontrada: '{query}'")

    @classmethod
    def obtener_precio(cls, consulta: str) -> dict:
        """Versión optimizada con caché y rate limiting"""
        try:
            # Paso 1: Verificar caché de precios
            cache_key = consulta.lower()
            if cache_key in cls._PRICE_CACHE:
                data, timestamp = cls._PRICE_CACHE[cache_key]
                if datetime.now() - timestamp < cls._PRICE_CACHE_TTL:
                    return data

            # Paso 2: Obtener ID de criptomoneda
            cripto_id = cls._get_crypto_id(consulta)
            
            # Paso 3: Obtener precio con rate limiting
            cls._enforce_rate_limit()
            price_url = f"{APIConfig.COINGECKO_URL}/simple/price?ids={cripto_id}&vs_currencies=usd&include_24hr_change=true"
            price_response = requests.get(
                price_url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            price_response.raise_for_status()
            price_data = price_response.json()
            
            if cripto_id not in price_data:
                raise ValueError("Datos de precio no recibidos")

            # Paso 4: Obtener metadatos
            crypto_info = next(c for c in cls._CRYPTO_LIST_CACHE if c['id'] == cripto_id)
            
            # Paso 5: Formatear respuesta
            resultado = {
                "nombre": crypto_info['name'],
                "simbolo": crypto_info['symbol'].upper(),
                "precio": float(price_data[cripto_id]["usd"]),
                "cambio_24h": float(price_data[cripto_id].get("usd_24h_change", 0)),
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            # Actualizar caché
            cls._PRICE_CACHE[cache_key] = (resultado, datetime.now())
            cls._current_delay = max(cls._BASE_DELAY, cls._current_delay * 0.9)  # Reducir delay si éxito
            
            return resultado

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                cls._current_delay = min(cls._MAX_DELAY, cls._current_delay * 2)
                logger.warning(f"Rate limit alcanzado. Delay aumentado a {cls._current_delay}s")
            raise ValueError(f"Error de API: {str(e)}")
        except Exception as e:
            logger.error(f"Error al procesar '{consulta}': {str(e)}")
            raise ValueError(f"No se pudo obtener precio para '{consulta}'")
