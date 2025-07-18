import os
import logging
import random
from pathlib import Path
from telegram.ext import Application

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Carga de variables de entorno
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# Variables esenciales
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id.strip()]
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def create_application():
    """Crea y configura la aplicación de Telegram"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN no está configurado")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.initialize()  # Inicialización explícita
    return application

class BotMeta:
    NAME = "SoonBot"
    VERSION = "2.0"
    DESCRIPTION = "Asistente de criptomonedas"
    
    @classmethod
    def full_name(cls):
        return f"{cls.NAME} v{cls.VERSION}"

class BotPersonality:
    CRYPTO_LIST = ["BTC", "ETH", "BNB", "SOL"]
    
    @staticmethod
    def get_ai_prompt():
        return {
            "role": "system",
            "content": "Eres un asistente de criptomonedas profesional pero cercano."
        }
