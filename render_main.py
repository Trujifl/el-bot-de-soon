# render_main.py - Versión definitiva con filtro IP
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

# Configuración IPs permitidas (Telegram + Render internas)
ALLOWED_NETS = [
    ipaddress.ip_network('149.154.160.0/20'),  # Telegram
    ipaddress.ip_network('91.108.4.0/22'),     # Telegram
    ipaddress.ip_network('127.0.0.0/8')        # Render health checks
]

# Filtro de IP seguro
@app.before_request
def filter_ips():
    client_ip = ipaddress.ip_address(request.remote_addr)
    if not any(client_ip in net for net in ALLOWED_NETS):
        logger.warning(f"Acceso denegado desde IP: {client_ip}")
        return "IP no autorizada", 403

# Configuración de la aplicación
application = Application.builder().token(TOKEN).build()

# Handlers esenciales
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    await update.message.reply_text(
        f"🚀 ¡Hola! Soy {BotMeta.NAME}\n"
        "Escribe /help para ver mis comandos"
    )

def setup_handlers():
    # Comandos básicos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    
    # Handlers personalizados
    setup_base_handlers(application)
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("post", PostHandler().handle))
    application.add_handler(CommandHandler("resumen_texto", ResumeHandler().handle_resumen_texto))
    application.add_handler(CommandHandler("resumen_url", ResumeHandler().handle_resumen_url))
    
    # Manejo de mensajes no reconocidos
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: u.message.reply_text("No entendí. Usa /help")
    ))

# Webhook mejorado
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = Update.de_json(await request.get_json(), application.bot)
        await application.process_update(update)
        return "", 200  # Respuesta vacía para ahorrar ancho de banda
    except Exception as e:
        logger.error(f"Error en webhook: {str(e)}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} operativo", 200

if __name__ == '__main__':
    setup_handlers()
    
    # Configuración de webhook para producción
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 10000)),
        webhook_url=os.getenv('WEBHOOK_URL'),
        secret_token=os.getenv('WEBHOOK_SECRET'),
        drop_pending_updates=True
    )
