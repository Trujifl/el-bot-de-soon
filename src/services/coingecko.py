import requests
from datetime import datetime
from src.config import APIConfig, logger

class CoinGeckoAPI:
    @staticmethod
    def obtener_precio(cripto_id: str) -> dict:
        """Obtiene el precio de una criptomoneda desde CoinGecko"""
        try:
            response = requests.get(
                f"{APIConfig.COINGECKO}/coins/{cripto_id}",
                timeout=APIConfig.COINGECKO_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "nombre": data["name"],
                "simbolo": data["symbol"],
                "precio": data["market_data"]["current_price"]["usd"],
                "cambio_24h": data["market_data"]["price_change_percentage_24h"],
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        except Exception as e:
            logger.error(f"Error en CoinGecko API: {e}")
            raise