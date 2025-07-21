import requests
from datetime import datetime
from src.config import APIConfig, logger

class CoinGeckoAPI:
    @staticmethod
    def obtener_precio(cripto_id: str) -> dict:
        """
        Obtiene el precio de una criptomoneda desde CoinGecko API
        
        Args:
            cripto_id (str): ID de la criptomoneda según CoinGecko (ej: 'bitcoin')
            
        Returns:
            dict: Diccionario con los datos del precio:
                - nombre: Nombre completo de la cripto
                - simbolo: Símbolo (ej: BTC)
                - precio: Precio actual en USD
                - cambio_24h: Porcentaje de cambio en 24h
                - ultima_actualizacion: Fecha y hora de la consulta
                
        Raises:
            ValueError: Si hay problemas con la API o los datos
        """
        try:
            # Primera llamada para obtener precio y cambio porcentual
            price_url = f"{APIConfig.COINGECKO_URL}/simple/price?ids={cripto_id}&vs_currencies=usd&include_24hr_change=true"
            logger.info(f"Consultando endpoint simple/price: {price_url}")
            
            price_response = requests.get(
                price_url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            price_response.raise_for_status()
            price_data = price_response.json()
            
            # Validar estructura básica de datos
            if cripto_id not in price_data or "usd" not in price_data[cripto_id]:
                raise ValueError("Estructura de datos de precio inválida")
            
            precio = float(price_data[cripto_id]["usd"])
            cambio_24h = float(price_data[cripto_id]["usd_24h_change"]) if "usd_24h_change" in price_data[cripto_id] else 0.0
            
            # Segunda llamada para obtener metadatos (nombre, símbolo)
            detail_url = f"{APIConfig.COINGECKO_URL}/coins/{cripto_id}"
            detail_response = requests.get(
                detail_url,
                timeout=APIConfig.COINGECKO_TIMEOUT,
                headers=APIConfig.REQUEST_HEADERS
            )
            detail_response.raise_for_status()
            detail_data = detail_response.json()
            
            # Validar datos importantes
            required_fields = ["name", "symbol", "market_data"]
            if not all(field in detail_data for field in required_fields):
                raise ValueError("Faltan campos esenciales en la respuesta")
            
            # Verificación adicional para precios irreales
            if precio > 1000000:  # Si el precio es > 1 millón (bitcoin no debería estar aquí)
                logger.warning(f"Precio potencialmente mal formateado recibido: {precio}")
                raise ValueError("Precio recibido parece incorrecto")
            
            return {
                "nombre": detail_data["name"],
                "simbolo": detail_data["symbol"].upper(),
                "precio": precio,
                "cambio_24h": cambio_24h,
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con CoinGecko API: {str(e)}")
            raise ValueError(f"No se pudo conectar a CoinGecko API: {str(e)}")
        except ValueError as e:
            logger.error(f"Error en datos recibidos: {str(e)}")
            raise ValueError(f"Datos de criptomoneda inválidos: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            raise ValueError(f"Error al obtener precio: {str(e)}")
