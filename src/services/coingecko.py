import requests
from datetime import datetime
from src.config import logger, APIConfig  # Import directo y explícito

class CoinGeckoAPI:
    @staticmethod
    def obtener_precio(cripto_id: str) -> dict:
        """Optimizado para producción en Render"""
        try:
            # Endpoint combinado para reducir llamadas API
            url = f"{APIConfig.COINGECKO_URL}/coins/{cripto_id}?tickers=false&market_data=true"
            logger.info(f"Consultando CoinGecko API: {url}")
            
            response = requests.get(
                url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            response.raise_for_status()
            data = response.json()

            # Validación de datos esenciales
            required_fields = ["name", "symbol", "market_data"]
            if not all(field in data for field in required_fields):
                raise ValueError("Respuesta API incompleta")

            market_data = data["market_data"]
            precio = float(market_data["current_price"]["usd"])
            cambio_24h = float(market_data["price_change_percentage_24h_in_currency"]["usd"])

            return {
                "nombre": data["name"],
                "simbolo": data["symbol"].upper(),
                "precio": precio,
                "cambio_24h": cambio_24h,
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error API: {str(e)}")
            raise ValueError(f"Error al conectar con CoinGecko: {str(e)}")
        except (KeyError, ValueError) as e:
            logger.error(f"Datos inválidos: {str(e)}")
            raise ValueError(f"Datos de criptomoneda inválidos: {str(e)}")
