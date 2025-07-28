from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import os
import logging
from src.config import TELEGRAM_TOKEN as TOKEN, logger, BotMeta
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler
from src.utils.filters import MentionedBotFilter, TopicFilter

app = Flask(__name__)
post_handler = PostHandler()
resume_handler = ResumeHandler()
application = Application.builder().token(TOKEN).build()

async def set_commands():
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("help", "Muestra ayuda"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto en español"),
        BotCommand("resumen_url", "Resume una página web en español")
    ]
    await application.bot.set_my_commands(commands)

# Handler adicional para responder en privado
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"¡Hola {update.effective_user.first_name}! 👋\n"
        f"¿En qué puedo ayudarte hoy?\n\n"
        f"Soy SoonBot, tu asistente experto en criptomonedas."
    )

async def handle_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Recibido: {update.message.text}")

def setup_handlers():
    setup_base_handlers(application)
    filtro = MentionedBotFilter() & TopicFilter()

    application.add_handler(CommandHandler("precio", precio_cripto, filters=filtro))
    application.add_handler(CommandHandler("post", post_handler.handle, filters=filtro))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto, filters=filtro))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url, filters=filtro))
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

    # Handlers internos para responder en privado
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_echo))

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        application.create_task(application.process_update(update))
        logger.info(f"[{BotMeta.NAME}] Update procesado")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} está activo ✅", 200

@app.route('/set_webhook')
def set_webhook():
    try:
        webhook_url = f"https://el-bot-de-soon.onrender.com/webhook"
        application.bot.set_webhook(webhook_url)
        return f"Webhook establecido en: {webhook_url}", 200
    except Exception as e:
        return f"Error al establecer webhook: {e}", 500

if __name__ == '__main__':
    setup_handlers()
    import asyncio
    asyncio.run(set_commands())
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
