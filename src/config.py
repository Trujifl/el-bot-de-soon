# config.py - Configuraciones centralizadas
import os
import logging
import random
from pathlib import Path
from pydantic_settings import BaseSettings  # ¡Actualizado!

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_errors.log')
    ]
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    OPENAI_API_KEY: str
    TELEGRAM_ADMIN_IDS: str
    TELEGRAM_CHANNEL_ID: str
    WEBHOOK_URL: str
    WEBHOOK_SECRET: str
    PORT: int = 10000

    class Config:
        env_file = ".env"  # Solo para desarrollo local

# Carga configuraciones
try:
    settings = Settings()
    TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    ADMIN_IDS = [int(id.strip()) for id in settings.TELEGRAM_ADMIN_IDS.split(",") if id.strip()]
    CHANNEL_ID = settings.TELEGRAM_CHANNEL_ID
    WEBHOOK_URL = settings.WEBHOOK_URL
    WEBHOOK_SECRET = settings.WEBHOOK_SECRET
    PORT = settings.PORT
except Exception as e:
    logger.error(f"Error cargando configuraciones: {e}")
    raise

# Clases de configuración
class BotMeta:
    NAME = "SoonBot"
    VERSION = "2.0"
    EMOJI = "🚀"
    DESCRIPTION = "Asistente de criptomonedas"

class BotPersonality:
    TONO = "Profesional pero cercano"
    CRIPTOS_COMUNES = ["bitcoin", "ethereum", "binancecoin", "solana"]
    
    PERSONALIDAD_IA = {
        "role": "system",
        "content": (
            "Eres SoonBot, un asistente especializado en criptomonedas con un tono profesional pero cercano. "
            "Tienes conocimientos avanzados sobre blockchain, trading y tecnología. "
            "Respondes de manera concisa pero informativa. "
            "Usas emojis relevantes (🚀 para oportunidades, ⚠️ para riesgos). "
            "Cuando hables de precios, menciona siempre la fuente (CoinGecko). "
            "Para preguntas técnicas, da ejemplos prácticos."
        )
    }
    
    @staticmethod
    def get_ia_prompt(user_message: str, username: str) -> list:
        return [
            BotPersonality.PERSONALIDAD_IA,
            {
                "role": "user",
                "content": f"{username} pregunta: {user_message}"
            }
        ]

    @staticmethod
    def get_random_saludo(nombre: str) -> str:
        saludos = [
            f"¡Hola {nombre}! ¿En qué puedo ayudarte hoy?",
            f"¡Buenos días {nombre}! Listo para operar 🚀"
        ]
        return random.choice(saludos)

class APIConfig:
    COINGECKO_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_TIMEOUT = 30
    REQUEST_HEADERS = {
        "User-Agent": "SoonBot/2.0",
        "Accept": "application/json"
    }
