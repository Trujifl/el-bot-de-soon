import requests
import os

class CoinMarketCapAPI:
    BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    API_KEY = os.getenv("COINMARKETCAP_API_KEY")

    @staticmethod
    def obtener_precio(nombre_token: str) -> dict | None:
        """
        Consulta el precio y variación de un token desde CoinMarketCap.
        Devuelve un diccionario con: nombre, símbolo, precio y cambio 24h.
        """
        if not CoinMarketCapAPI.API_KEY:
            print("❌ No se encontró la API KEY de CoinMarketCap.")
            return None

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": CoinMarketCapAPI.API_KEY,
        }

        params = {
            "symbol": nombre_token.upper(), 
            "convert": "USD"
        }

        try:
            response = requests.get(CoinMarketCapAPI.BASE_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            symbol = nombre_token.upper()
            if "data" in data and symbol in data["data"]:
                info = data["data"][symbol]
                quote = info["quote"]["USD"]
                return {
                    "nombre": info["name"],
                    "symbol": symbol,
                    "precio": round(quote["price"], 2),
                    "cambio_24h": round(quote["percent_change_24h"], 2)
                }

        except requests.exceptions.RequestException as e:
            print(f"❌ Error al consultar CoinMarketCap: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

        return None
