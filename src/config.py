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

# Configuración obligatoria para Render
class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    OPENAI_API_KEY: str
    TELEGRAM_CHANNEL_ID: str
    WEBHOOK_URL: str
    WEBHOOK_SECRET: str
    PORT: int = 10000

    class Config:
        case_sensitive = True

# Validación estricta (sin .env)
try:
    settings = Settings()
    TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    CHANNEL_ID = settings.TELEGRAM_CHANNEL_ID
    WEBHOOK_URL = settings.WEBHOOK_URL
    WEBHOOK_SECRET = settings.WEBHOOK_SECRET
    PORT = settings.PORT
except Exception as e:
    logger.error(f"Error crítico en configuración: {e}")
    raise

class BotMeta:
    NAME = "SoonBot"
    VERSION = "2.0"
