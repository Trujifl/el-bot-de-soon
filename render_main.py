import os
import asyncio
import logging

from telegram import BotCommand, BotCommandScopeDefault, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.handlers.base import start, help_command
from src.handlers.token_query import setup_token_query_handler, precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler
from src.utils.filters import MentionedBotFilter, TopicFilter
from src.config import TELEGRAM_TOKEN, WEBHOOK_URL, POST_CHANNEL_ID

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
resume_handler = ResumeHandler()
post_handler = PostHandler()
post_handler.CHANNEL_ID = POST_CHANNEL_ID

async def handle_invoked_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

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
        await update.message.reply_text(
            "🤖 Comandos disponibles:\n/start, /help, /precio, /post, /resumen_texto, /resumen_url"
        )

async def set_commands():
    commands = [
        BotCommand("start", "Iniciar el bot"),
        BotCommand("help", "Ver ayuda"),
        BotCommand("precio", "Consultar precio de un token"),
        BotCommand("post", "Generar un post automático"),
        BotCommand("resumen_texto", "Resumir un texto"),
        BotCommand("resumen_url", "Resumir una web")
    ]
    await application.bot.set_my_commands(commands, scope=BotCommandScopeDefault())

def setup_handlers():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    setup_token_query_handler(application)

    application.add_handler(CommandHandler("post", post_handler.handle))
    application.add_handler(MessageHandler(filters.CallbackQuery, post_handler.handle_confirmation))

    # Solo responder si es mencionado y en el topic correcto
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & MentionedBotFilter() & TopicFilter(),
        handle_invoked_command
    ))

    # Ignora cualquier mensaje que no esté mencionado o fuera del topic
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda update, context: None
    ))

async def main():
    await set_commands()
    setup_handlers()

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path="",
        webhook_url=WEBHOOK_URL,
    )
    await application.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
