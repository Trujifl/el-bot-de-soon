from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackContext
from src.config import logger, BotPersonality
from src.utils.personality import Personalidad
from src.services.openai import generar_respuesta_ia


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador de /start (mejorado)"""
    try:
        user = update.effective_user
        await update.message.reply_text(
            f"¡Hola {user.first_name}! Soy {BotPersonality.NAME}\n\n"
            "Escribe algo como:\n"
            "- 'hola'\n"
            "- 'precio de bitcoin'\n"
            "- /help para ayuda",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error en start: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nueva función dedicada para /help"""
    await update.message.reply_text(
        "ℹ️ Comandos disponibles:\n"
        "/start - Mensaje de bienvenida\n"
        "/precio [cripto] - Consultar precios\n\n"
        "También puedes preguntar normalmente como:\n"
        "'¿Cómo está bitcoin hoy?'",
        parse_mode="Markdown"
    )
async def mensaje_generico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Versión simplificada para depuración"""
    try:
        logger.info(f"Mensaje recibido: {update.message.text}")  # Log importante
        
        texto = update.message.text.lower()
        user_name = update.effective_user.first_name
        
        if any(palabra in texto for palabra in ["hola", "hi", "buenas"]):
            await update.message.reply_text(
                f"¡Hola {user_name}! ¿Cómo estás? 😊"
            )
        else:
            await update.message.reply_text(
                f"{user_name}, no entendí. Prueba con /help",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error en mensaje_generico: {e}")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador para comandos desconocidos"""
    await update.message.reply_text(
        "⚠️ Comando no reconocido. Prueba con /help",
        parse_mode="Markdown"
    )

class BaseHandler:
    async def handle(self, update: Update, context: CallbackContext) -> None:
        raise NotImplementedError("Los manejadores deben implementar este método")
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador mejorado para mensajes no comandos"""
    try:
        user_message = update.message.text.lower().strip()  # Limpia espacios
        user_name = update.effective_user.first_name
        
        # 1. Primero verifica saludos coloquiales
        saludos = {
            'epaa': True,
            'epa': True,
            'wenaas': True,
            'wenas': True,
            'hola': True,
            'buenas': True
        }
        
        if user_message in saludos:
            respuesta = Personalidad.generar_saludo(user_name)
            await update.message.reply_text(respuesta)
            return
            
        # 2. Si no es saludo, usa OpenAI
        respuesta = await generar_respuesta_ia(user_message, user_name)
        if respuesta:
            await update.message.reply_text(respuesta)
        else:
            await update.message.reply_text(
                f"{user_name}, no entendí. Prueba con /help"
            )
            
    except Exception as e:
        logger.error(f"Error en handle_message: {e}")
        await update.message.reply_text(
            "⚠️ Ups, algo falló. Intenta de nuevo"
        )

def setup_base_handlers(application):
    """Configura el handler para mensajes no comandos"""
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

