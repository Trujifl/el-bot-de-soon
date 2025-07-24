import asyncio
from flask import Flask, request
from telegram import Update, BotCommand, BotCommandScope
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
    logger,
    BotMeta
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

async def topic_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return
    if not (
        message.chat.id == GROUP_ID and
        message.is_topic_message and
        message.message_thread_id == TOPIC_ID
    ):
        return

application.add_handler(MessageHandler(filters.ALL, topic_guard), group=0)

class MentionedBotFilter(filters.BaseFilter):
    def filter(self, message):
        if not message or not message.text:
            return False
        if message.entities:
            return any(
                e.type == "mention" and message.text.startswith("@")
                for e in message.entities
            )
        return False

async def handle_invoked_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    username = context.bot.username.lower()

    # Remover @botname
    if text.startswith(f"@{username}"):
        text = text.replace(f"@{username}", "").strip()

    if text.startswith("/precio"):
        await precio_cripto(update, context)
    elif text.startswith("/post"):
        await post_handler.handle(update, context)
    elif text.startswith("/resumen_texto"):
        await resume_handler.handle_resumen_texto(update, context)
    elif text.startswith("/resumen_url"):
        await resume_handler.handle_resumen_url(update, context)
    elif text.startswith("/start"):
        await start(update, context)
    elif text.startswith("/help"):
        await help_command(update, context)
    else:
        await update.message.reply_text("❌ Comando no reconocido o mal escrito.")

application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

application.add_handler(
    MessageHandler(filters.TEXT & MentionedBotFilter() & TopicFilter(), handle_invoked_command)
)

class TopicFilter(filters.BaseFilter):
    def filter(self, message):
        return (
            message.chat.id == GROUP_ID and
            message.is_topic_message and
            message.message_thread_id == TOPIC_ID
        )

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        await application.update_queue.put(Update.de_json(request.get_json(force=True), application.bot))
        return "ok"

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

async def main():
    await set_commands()
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=f"{BotMeta.URL}/{TOKEN}"
    )

if __name__ == "__main__":
    asyncio.run(main())
