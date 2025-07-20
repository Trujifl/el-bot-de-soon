import os
import logging
from pydantic_settings import BaseSettings

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuración obligatoria con validación
class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    OPENAI_API_KEY: str
    TELEGRAM_CHANNEL_ID: str
    WEBHOOK_URL: str
    WEBHOOK_SECRET: str
    PORT: int = 10000
    TELEGRAM_ADMIN_IDS: str

    class Config:
        case_sensitive = True

# Carga y validación
try:
    settings = Settings()
    TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    CHANNEL_ID = settings.TELEGRAM_CHANNEL_ID
    WEBHOOK_URL = settings.WEBHOOK_URL
    WEBHOOK_SECRET = settings.WEBHOOK_SECRET
    PORT = settings.PORT
    ADMIN_IDS = [int(id.strip()) for id in settings.TELEGRAM_ADMIN_IDS.split(",") if id.strip()]
except Exception as e:
    logger.error(f"Error en configuración: {e}")
    raise

# Configuraciones de API
class APIConfig:
    COINGECKO_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_TIMEOUT = 30
    REQUEST_HEADERS = {
        "User-Agent": "SoonBot/2.0",
        "Accept": "application/json"
    }

# Metadata del Bot
class BotMeta:
    NAME = "SoonBot"
    VERSION = "2.0"
    DESCRIPTION = "Asistente de criptomonedas"
