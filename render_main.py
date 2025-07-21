# render_main.py - Versión final para producción en Render
from flask import Flask, request, Response
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import asyncio
import logging
import ipaddress
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    PORT,
    logger,
    BotMeta
)
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler

# Configuración inicial
app = Flask(__name__)
post_handler = PostHandler()
resume_handler = ResumeHandler()

# Rangos IP oficiales de Telegram (para filtrado)
TELEGRAM_IPS = [
    ipaddress.ip_network('149.154.160.0/20'),
    ipaddress.ip_network('91.108.4.0/22')
]

# Instancia de la aplicación de Telegram
application = Application.builder().token(TOKEN).updater(None).build()

# Filtro de seguridad por IP
@app.before_request
def verify_ip():
    client_ip = ipaddress.ip_address(request.remote_addr)
    if not any(client_ip in net for net in TELEGRAM_IPS):
        logger.warning(f"Intento de acceso desde IP no autorizada: {client_ip}")
        return "Acceso no autorizado", 403

# Configuración de comandos del bot
async def set_commands():
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto con IA"),
        BotCommand("resumen_url", "Resume una página web con IA")
    ]
    await application.bot.set_my_commands(commands)

# Configuración de handlers
def setup_handlers():
    setup_base_handlers(application)
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("post", post_handler.handle))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

# Endpoint del webhook optimizado
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not request.json:
            logger.warning("Solicitud sin JSON recibida")
            return Response("Datos inválidos", status=400)

        update = Update.de_json(request.json, application.bot)
        
        async def process_update():
            try:
                await application.update_queue.put(update)
                logger.info(f"Procesado update {update.update_id}")
                return "OK", 200
            except Exception as e:
                logger.error(f"Error al procesar update: {str(e)}")
                return "Error interno", 500

        response, status = asyncio.run(process_update())
        return Response(response, status=status, content_type='text/plain')

    except Exception as e:
        logger.error(f"Error en webhook: {str(e)}")
        return Response("Error en el servidor", status=500)

# Health check
@app.route('/')
def health_check():
    return f"{BotMeta.NAME} operativo ✅", 200

# Inicialización
if __name__ == '__main__':
    setup_handlers()
    asyncio.run(set_commands())  # Configura comandos al iniciar
    
    application.run_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        webhook_url=f"https://el-bot-de-soon.onrender.com/webhook",
        drop_pending_updates=True
    )
