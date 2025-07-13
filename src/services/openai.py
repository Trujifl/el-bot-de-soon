import openai
import logging
from typing import Optional
from src.config import OPENAI_API_KEY, BotMeta, BotPersonality  # Cambio clave aquí

logger = logging.getLogger(__name__)

async def generar_respuesta_ia(mensaje: str, nombre_usuario: str) -> Optional[str]:
    """Versión corregida usando los atributos correctos"""
    try:
        if not OPENAI_API_KEY:
            logger.error("API key de OpenAI no configurada")
            return None

        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": f"Eres {BotMeta.NAME}, un bot de criptomonedas. "  # Usa BotMeta
                              f"Personalidad: {BotPersonality.TONO}. "
                              "Responde de manera profesional pero cercana."
                },
                {
                    "role": "user",
                    "content": f"{nombre_usuario}: {mensaje}"
                }
            ],
            temperature=0.7,
            max_tokens=150
        )
        system_prompt = (
    f"Eres {BotMeta.NAME}. Actúa exactamente con esta personalidad:\n"
    f"- Tono: {BotPersonality.TONO}\n"
    f"- Emojis: Usa {BotMeta.EMOJI} ocasionalmente\n"
    f"- Modismos: Usa términos como 'crack', 'socio', 'juega vivo'\n"
    "Mantén respuestas breves (1-2 frases)."
)
        return response.choices[0].message.content
        
        
    except Exception as e:
        logger.error(f"Error en OpenAI: {str(e)}")
        return f"¡Ups {nombre_usuario}! Algo falló. Intenta de nuevo más tarde."