from flask import Flask, request, Response
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
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

# Configuración inicial
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

# Creamos una instancia de Application
def create_application():
    application = Application.builder().token(TOKEN).build()
    
    # Handlers básicos
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"¡Hola! Soy {BotMeta.NAME} {BotMeta.EMOJI}")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: u.message.reply_text("Usa /start para comenzar")
    ))
    
    return application

# Variable global para la aplicación
application = create_application()

# Webhook corregido con inicialización segura
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        if not application.running:
            await application.initialize()
            await application.start()
            
        json_data = request.get_json()
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return "", 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} ✅", 200

async def run_webhook():
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 10000)),
        webhook_url=os.getenv('WEBHOOK_URL'),
        secret_token=os.getenv('WEBHOOK_SECRET'),
        drop_pending_updates=True
    )
    await asyncio.Event().wait()  # Ejecución infinita

if __name__ == '__main__':
    try:
        asyncio.run(run_webhook())
    except KeyboardInterrupt:
        logger.info("Deteniendo el bot...")
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}", exc_info=True)
    finally:
        asyncio.run(application.stop())
