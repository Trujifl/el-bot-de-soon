import requests
from fuzzywuzzy import fuzz  # Para búsqueda aproximada
from datetime import datetime, timedelta
from src.config import APIConfig, logger

class CoinGeckoAPI:
    # Cache para lista de criptos (actualización cada 12 horas)
    _CRYPTO_LIST_CACHE = None
    _CRYPTO_LIST_LAST_UPDATED = None
    _CRYPTO_LIST_TTL = timedelta(hours=12)

    @classmethod
    def _get_all_cryptos(cls):
        """Obtiene todas las criptomonedas de CoinGecko con cache"""
        if cls._CRYPTO_LIST_CACHE and datetime.now() - cls._CRYPTO_LIST_LAST_UPDATED < cls._CRYPTO_LIST_TTL:
            return cls._CRYPTO_LIST_CACHE

        url = f"{APIConfig.COINGECKO_URL}/coins/list"
        response = requests.get(url, timeout=APIConfig.COINGECKO_TIMEOUT)
        response.raise_for_status()
        
        cls._CRYPTO_LIST_CACHE = response.json()
        cls._CRYPTO_LIST_LAST_UPDATED = datetime.now()
        return cls._CRYPTO_LIST_CACHE

    @classmethod
    def _find_best_match(cls, query: str):
        """Encuentra la mejor coincidencia para una consulta"""
        cryptos = cls._get_all_cryptos()
        query = query.lower().strip()
        
        best_match = None
        best_score = 0
        
        for crypto in cryptos:
            # Busca en nombre (bitcoin), símbolo (btc) e id (bitcoin)
            name_score = fuzz.ratio(query, crypto["name"].lower())
            symbol_score = fuzz.ratio(query, crypto["symbol"].lower())
            id_score = fuzz.ratio(query, crypto["id"].lower())
            
            current_score = max(name_score, symbol_score, id_score)
            if current_score > best_score:
                best_score = current_score
                best_match = crypto
                if best_score == 100:  # Coincidencia perfecta
                    break
        
        return best_match if best_score >= 50 else None  # Umbral mínimo 50%

    @classmethod
    def obtener_precio(cls, consulta: str) -> dict:
        """Versión mejorada que reconoce cualquier cripto"""
        try:
            # Paso 1: Buscar la mejor coincidencia
            crypto_match = cls._find_best_match(consulta)
            if not crypto_match:
                raise ValueError(f"Cripto no encontrada: '{consulta}'")
            
            # Paso 2: Obtener precio (tu implementación actual)
            cripto_id = crypto_match["id"]
            price_url = f"{APIConfig.COINGECKO_URL}/simple/price?ids={cripto_id}&vs_currencies=usd&include_24hr_change=true"
            price_data = requests.get(price_url, timeout=APIConfig.COINGECKO_TIMEOUT).json()
            
            if cripto_id not in price_data:
                raise ValueError("Datos de precio no disponibles")
            
            return {
                "nombre": crypto_match["name"],
                "simbolo": crypto_match["symbol"].upper(),
                "precio": float(price_data[cripto_id]["usd"]),
                "cambio_24h": float(price_data[cripto_id].get("usd_24h_change", 0)),
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de API: {str(e)}")
            raise ValueError("Error al conectar con CoinGecko")
        except Exception as e:
            logger.error(f"Error al procesar '{consulta}': {str(e)}")
            raise ValueError(f"No se pudo obtener precio para '{consulta}'")
