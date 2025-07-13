# src/config.py
"""
CONFIGURACIÓN CENTRALIZADA DEL BOT

Se divide en:
1. Variables de entorno (.env)
2. Constantes del bot
3. Configuración de APIs externas
"""

import os
import logging
import random
import dotenv
from pathlib import Path
from telegram.ext import MessageHandler, filters
from typing import List
from dotenv import load_dotenv

# =============================================================================
# 1. CONFIGURACIÓN INICIAL DEL SISTEMA
# =============================================================================

# Setup básico de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_errors.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Carga variables de entorno
load_dotenv(dotenv_path=Path(".env"))

# =============================================================================
# 2. VARIABLES DE ENTORNO (requieren .env)
# =============================================================================

# Configuración esencial
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    logger.error("Falta TELEGRAM_TOKEN en .env")
    raise ValueError("Token de Telegram no configurado")

# Configuración de administradores
ADMIN_IDS: List[int] = [
    int(id.strip()) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") 
    if id.strip()
]

raw_channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
CHANNEL_ID = raw_channel_id if raw_channel_id.startswith(("@", "-100")) else None

# Configuración opcional
CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")



env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Configuración para despliegue
RENDER = os.getenv("RENDER", "false").lower() == "true"  
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://tu-bot.onrender.com")
PORT = int(os.getenv("PORT", "10000"))

# =============================================================================
# 3. CONSTANTES DEL BOT (configuración estática)
# =============================================================================

class BotMeta:
    NAME: str = "SoonBot"
    VERSION: str = "9.4"
    EMOJI: str = "🚀"
    DESCRIPTION: str = "Asistente experto en criptomonedas"

class BotPersonality:
    TONO: str = "Profesional pero cercano"
    CRIPTOS_COMUNES: List[str] = [
        "bitcoin", 
        "ethereum",
        "binancecoin",
        "solana"
    ]
    
    @staticmethod
    def get_random_saludo(nombre: str) -> str:
        saludos = [
            f"¡Epa {nombre}! ¿Cómo anda? 👋",
            f"¡Buenaas {nombre}! ¿En qué te ayudo? 🔥"
        ]
        return random.choice(saludos)

# =============================================================================
# 4. CONFIGURACIÓN DE APIS EXTERNAS
# =============================================================================

class APIConfig:
    COINGECKO: str = "https://api.coingecko.com/api/v3"
    COINGECKO_TIMEOUT: int = 10  # segundos
    
    @staticmethod
    def get_openai_config() -> dict:
        return {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }

# =============================================================================
# 5. CONFIGURACIÓN DE HANDLERS 
# =============================================================================

class HandlerConfig:
    """Configuración centralizada de los handlers del bot"""
    
    @staticmethod
    def setup_handlers(application):
        """
        Registra todos los handlers en el orden correcto.
        IMPORTANTE: El MessageHandler debe ir primero.
        """
        from src.handlers import (  # Importar aquí para evitar circular imports
            mensaje_generico,
            start
        )
        from telegram.ext import CommandHandler
        
        # 1. Handler para mensajes regulares (DEBE IR PRIMERO)
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                mensaje_generico
            )
        )
        
        # 2. Handlers de comandos
        application.add_handler(CommandHandler("start", start))
        # ... agregar otros handlers aquí

# =============================================================================
# 6. VALIDACIÓN INICIAL
# =============================================================================

if __name__ == "__main__":
    # Verificación básica al importar
    logger.info(f"✅ Configuración cargada para {BotMeta.NAME} v{BotMeta.VERSION}")
    logger.info(f"🔑 Token length: {len(TELEGRAM_TOKEN)} caracteres")
    if OPENAI_API_KEY:
        logger.info("🤖 OpenAI integrado")
    else:
        logger.warning("⚠️ OpenAI no configurado")