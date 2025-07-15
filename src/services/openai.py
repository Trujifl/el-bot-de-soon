import openai
from src.config import OPENAI_API_KEY, BotPersonality, logger

async def generar_respuesta_ia(mensaje: str, nombre_usuario: str) -> str:
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY no está configurada")
        return f"¡Lo siento {nombre_usuario}! Mi servicio de IA no está disponible en este momento."
    
    try:
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=BotPersonality.get_ia_prompt(mensaje, nombre_usuario),
            temperature=0.7
        )
        return response.choices[0].message.content
        
    except openai.APIError as e:
        logger.error(f"Error de API OpenAI: {str(e)}")
        return f"⚠️ {nombre_usuario}, hubo un problema con el servicio de IA. Por favor intenta más tarde."
        
    except Exception as e:
        logger.error(f"Error inesperado en IA: {str(e)}")
        return f"¡Vaya {nombre_usuario}! Algo salió mal. ¿Podrías reformular tu pregunta?"