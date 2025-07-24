import asyncio
from flask import Flask, request
from telegram import Update, BotCommand, BotCommandScopeChat
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import os

from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    logger
)

from src.handlers.base import start, help_command
from src.handlers.crypto import precio_cripto
from src.handlers.resume import ResumeHandler
from src.handlers.token_query import handle_consulta_token
from src.handlers.post import PostHandler

app = Flask(__name__)
post_handler = PostHandler()
resume_handler = ResumeHandler()

application = Application.builder().token(TOKEN).build()

GROUP_ID = -1002348706229
TOPIC_ID = 8183
POST_CHANNEL_ID = -1002615396578

# ✅ Filtro: solo permite mensajes del grupo y topic autorizados
class TopicFilter(filters.BaseFilter):
    def filter(self, message):
        return (
            messa
