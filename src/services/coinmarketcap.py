import requests
import os

class CoinMarketCapAPI:
    BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    API_KEY = os.getenv("COINMARKETCAP_API_KEY")

    @staticmethod
    def obtener_precio(nombre_token: str) -> dict | None:
        if not CoinMarketCapAPI.API_KEY:
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

            if "data" in data and nombre_token.upper() in data["data"]:
                info = data["data"][nombre_token.upper()]
                return {
                    "nombre": info["name"],
                    "symbol": info["symbol"],
                    "precio": info["quote"]["USD"]["price"],
                    "cambio_24h": info["quote"]["USD"]["percent_change_24h"],
                }
        except Exception as e:
            print(f"❌ Error al consultar CoinMarketCap: {e}")

        return None
