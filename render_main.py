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
from src.handlers.base import setup_base_handlers, handle_message
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

def strict_topic_check(message):
    return (
        message.chat.id == GROUP_ID and
        message.is_topic_message and
        message.message_thread_id == TOPIC_ID
    )

def setup_handlers():
    setup_base_handlers(application)

    post_handler.CHANNEL_ID = POST_CHANNEL_ID

    application.add_handler(CommandHandler("precio", precio_cripto, filters=TopicFilter()))
    application.add_handler(CommandHandler("post", post_handler.handle, filters=TopicFilter()))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto, filters=TopicFilter()))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url, filters=TopicFilter()))
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & TopicFilter(), handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & TopicFilter(), handle_consulta_token))

    application.add_handler(MessageHandler(filters.ALL, lambda u, c: None))

    try:
        asyncio.get_event_loop().create_task(set_commands())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(set_commands())

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        await application.update_queue.put(update)
        logger.info(f"[{BotMeta.NAME}] Update procesado")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} está activo ✅", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

if __name__ == '__main__':
    setup_handlers()
    iniciar_actualizador()

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        webhook_url=os.getenv("WEBHOOK_URL")
    )
