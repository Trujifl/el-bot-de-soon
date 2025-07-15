from telegram import Update
from telegram.ext import ContextTypes, CallbackContext, CommandHandler, MessageHandler, filters
from src.config import logger, BotPersonality
from src.services import openai

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    saludo = BotPersonality.get_random_saludo(user.first_name)
    await update.message.reply_text(
        f"{saludo}\n\nSoy {BotPersonality.NAME}, {BotPersonality.DESCRIPTION}",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Comandos disponibles:\n"
        "/start - Mensaje de bienvenida\n"
        "/precio [cripto] - Consultar precios\n"
        "/post - Crear publicación\n"
        "/resumen_texto - Resumir texto",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        respuesta = await openai.generar_respuesta_ia(
            update.message.text,
            update.effective_user.first_name
        )
        await update.message.reply_text(respuesta)
    except Exception as e:
        logger.error(f"Error en mensaje: {str(e)}")
        await update.message.reply_text("⚠️ Error al procesar tu mensaje")

def setup_base_handlers(application):
    """Configura los handlers básicos del bot"""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))