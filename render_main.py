# render_main.py - Versión final funcionando
from flask import Flask, request, Response
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
import asyncio
import logging
import ipaddress
import os
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    logger,
    BotMeta
)
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler

app = Flask(__name__)

# Rangos IP permitidos
ALLOWED_NETS = [
    ipaddress.ip_network('149.154.160.0/20'),  # Telegram
    ipaddress.ip_network('91.108.4.0/22'),     # Telegram
    ipaddress.ip_network('127.0.0.0/8')        # Render
]

# Filtro de IP
@app.before_request
def filter_ips():
    client_ip = ipaddress.ip_address(request.remote_addr)
    if not any(client_ip in net for net in ALLOWED_NETS):
        logger.warning(f"Acceso denegado desde IP: {client_ip}")
        return "IP no autorizada", 403

# Inicialización correcta de la aplicación
application = None

async def initialize_app():
    global application
    application = Application.builder().token(TOKEN).build()
    
    # Configuración de handlers
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"¡Hola! Soy {BotMeta.NAME} {BotMeta.EMOJI}")

    application.add_handler(CommandHandler("start", start))
    setup_base_handlers(application)
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("post", PostHandler().handle))
    application.add_handler(CommandHandler("resumen_texto", ResumeHandler().handle_resumen_texto))
    application.add_handler(CommandHandler("resumen_url", ResumeHandler().handle_resumen_url))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: u.message.reply_text("Usa /help para ver comandos")
    ))

    await application.initialize()  # Inicialización explícita
    await application.start()
    return application

# Webhook corregido
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        json_data = request.get_json()
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return "", 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} ✅", 200

if __name__ == '__main__':
    # Inicialización asíncrona correcta
    loop = asyncio.get_event_loop()
    application = loop.run_until_complete(initialize_app())
    
    # Configuración webhook
    loop.run_until_complete(application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 10000)),
        webhook_url=os.getenv('WEBHOOK_URL'),
        secret_token=os.getenv('WEBHOOK_SECRET'),
        drop_pending_updates=True
    ))
    loop.run_forever()
