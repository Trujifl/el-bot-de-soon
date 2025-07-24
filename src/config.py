import os
import logging
import random
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_errors.log')
    ]
)
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id.strip()]
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
GROUP_ID = -1002348706229
TOPIC_ID = 8183
POST_CHANNEL_ID = -1002615396578
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

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

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN no está configurado en .env")
