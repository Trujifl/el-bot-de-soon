# src/config.py
import os
import logging
import random
from pathlib import Path
from typing import List

# Setup básico de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_errors.log')
    ]
)
logger = logging.getLogger(__name__)

# Carga variables de entorno
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

# Variables de configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id.strip()]
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
RENDER = os.getenv("RENDER", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://tu-bot.onrender.com")
PORT = int(os.getenv("PORT", "5000"))

# Clases de configuración
class BotMeta:
    NAME = "SoonBot"
    VERSION = "9.4"
    EMOJI = "🚀"
    DESCRIPTION = "Asistente experto en criptomonedas"

class BotPersonality:
    TONO = "Profesional pero cercano"
    CRIPTOS_COMUNES = ["bitcoin", "ethereum", "binancecoin", "solana"]
    
    @staticmethod
    def get_random_saludo(nombre: str) -> str:
        saludos = [
            f"¡Epa {nombre}! ¿Cómo anda? 👋",
            f"¡Buenaas {nombre}! ¿En qué te ayudo? 🔥"
        ]
        return random.choice(saludos)

# Añadiendo la clase APIConfig que faltaba
class APIConfig:
    COINGECKO_URL = "https://api.coingecko.com/api/v3"
    OPENAI_TIMEOUT = 30
    REQUEST_HEADERS = {
        "User-Agent": "SoonBot/9.4",
        "Accept": "application/json"
    }

# Validación de configuración
if not TELEGRAM_TOKEN:
    logger.error("Falta TELEGRAM_TOKEN en .env")
    raise ValueError("Token de Telegram no configurado")

if __name__ == "__main__":
    logger.info(f"Configuración cargada para {BotMeta.NAME} v{BotMeta.VERSION}")