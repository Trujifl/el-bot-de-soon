import openai
from typing import Optional, Dict
from src.config import OPENAI_API_KEY, logger
from src.utils.personality import Personalidad

async def generar_respuesta_ia(
    mensaje: str,
    nombre_usuario: str,
    contexto: Optional[Dict] = None
) -> str:
    """
    Genera respuestas usando OpenAI con el estilo de SoonBot.
    
    Args:
        mensaje: Texto del usuario
        nombre_usuario: Nombre para personalización
        contexto: Diccionario con datos relevantes (ej: {'bitcoin': {'precio': 50000}})
    
    Returns:
        str: Respuesta generada con personalidad
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY no configurada")
        return Personalidad.generar_respuesta_error(nombre_usuario)

    try:
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        messages = [{
            "role": "system",
            "content": Personalidad.get_instructions(contexto)
        }, {
            "role": "user",
            "content": f"{nombre_usuario} pregunta: {mensaje}"
        }]

        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.7,  # Balance entre creatividad y precisión
            max_tokens=200,
            top_p=0.9
        )
        
        return response.choices[0].message.content
        
    except openai.APIConnectionError as e:
        logger.error(f"Error de conexión: {e}")
        return "🔌 Problema de conexión. Por favor, intenta más tarde."
    except Exception as e:
        logger.error(f"Error en OpenAI: {e}")
        return Personalidad.generar_respuesta_error(nombre_usuario)