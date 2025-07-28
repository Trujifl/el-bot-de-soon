from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import os
from src.config import TELEGRAM_TOKEN as TOKEN, logger, BotMeta
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler
from src.utils.filters import MentionedBotFilter, TopicFilter

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()
post_handler = PostHandler()
resume_handler = ResumeHandler()

def setup_handlers():
    setup_base_handlers(application)
    filtro = MentionedBotFilter() & TopicFilter()

    application.add_handler(CommandHandler("precio", precio_cripto, filters=filtro))
    application.add_handler(CommandHandler("post", post_handler.handle, filters=filtro))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto, filters=filtro))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url, filters=filtro))
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} está activo ✅", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        application.update_queue.put_nowait(update)
        logger.info(f"[{BotMeta.NAME}] Update procesado")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return "Error", 500

if __name__ == '__main__':
    import asyncio

    async def startup():
        await application.bot.set_webhook("https://el-bot-de-soon.onrender.com/webhook")
        commands = [
            BotCommand("start", "Inicia el bot"),
            BotCommand("help", "Muestra ayuda"),
            BotCommand("precio", "Consulta precio de cripto"),
            BotCommand("post", "Crea un post para el canal"),
            BotCommand("resumen_texto", "Resume un texto en español"),
            BotCommand("resumen_url", "Resume una página web en español")
        ]
        await application.bot.set_my_commands(commands)

    setup_handlers()
    asyncio.run(startup())
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
