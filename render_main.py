from flask import Flask
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from telegram import BotCommand
import asyncio
import os
from src.config import TELEGRAM_TOKEN as TOKEN, logger, BotMeta
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler
from src.utils.filters import MentionedBotFilter, TopicFilter

app = Flask(__name__)

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} está activo ✅", 200

application = Application.builder().token(TOKEN).build()
post_handler = PostHandler()
resume_handler = ResumeHandler()

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

def setup_handlers():
    setup_base_handlers(application)
    filtro = MentionedBotFilter() & TopicFilter()
    application.add_handler(CommandHandler("precio", precio_cripto, filters=filtro))
    application.add_handler(CommandHandler("post", post_handler.handle, filters=filtro))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto, filters=filtro))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url, filters=filtro))
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

if __name__ == '__main__':
    setup_handlers()
    loop = asyncio.get_event_loop()
    loop.create_task(set_commands())
    loop.create_task(application.run_polling())
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
