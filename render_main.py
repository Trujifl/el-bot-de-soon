import asyncio
from flask import Flask, request
from telegram import Update, BotCommand, BotCommandScope
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import os
import threading

from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    logger,
    BotMeta
)

from src.handlers.base import start, help_command, handle_message
from src.handlers.crypto import precio_cripto
from src.handlers.resume import ResumeHandler
from src.handlers.token_query import handle_consulta_token
from src.handlers.post import PostHandler

from src.services.price_updater import iniciar_actualizador

app = Flask(__name__)
post_handler = PostHandler()
resume_handler = ResumeHandler()

application = Application.builder().token(TOKEN).build()

GROUP_ID = -1002348706229
TOPIC_ID = 8183
POST_CHANNEL_ID = -1002615396578

# Middleware global para evitar mensajes fuera del topic
async def topic_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return
    if not (
        message.chat.id == GROUP_ID and
        message.is_topic_message and
        message.message_thread_id == TOPIC_ID
    ):
        return  # Bloquea todo lo que no sea del topic

application.add_handler(MessageHandler(filters.ALL, topic_guard), group=0)

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
    await application.bot.set_my_commands(commands, scope=BotCommandScope(chat_id=GROUP_ID))

class TopicFilter(filters.BaseFilter):
    def filter(self, message):
        return (
            message.chat.id == GROUP_ID and
            message.is_topic_message and
            message.message_thread_id == TOPIC_ID
        )

def setup_handlers():
    post_handler.CHANNEL_ID = POST_CHANNEL_ID

    # Comandos globales (permitidos fuera del topic)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Comandos protegidos por TopicFilter
    application.add_handler(CommandHandler("precio", precio_cripto, filters=TopicFilter()))
    application.add_handler(CommandHandler("post", post_handler.handle, filters=TopicFilter()))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto, filters=TopicFilter()))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url, filters=TopicFilter()))

    # Confirmación de posts
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

    # Texto libre protegido por topic
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & TopicFilter(), handle_message), block=True)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & TopicFilter(), handle_consulta_token), block=True)

setup_handlers()

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        await applica
