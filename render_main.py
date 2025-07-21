from flask import Flask, request, Response
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler
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

app = Flask(__name__)

# Rangos IP permitidos (Telegram + Render internas)
ALLOWED_IPS = [
    ipaddress.ip_network('149.154.160.0/20'),  # Telegram
    ipaddress.ip_network('91.108.4.0/22'),     # Telegram
    ipaddress.ip_network('127.0.0.0/8')        # Localhost (Render internas)
]

# Configuración de la aplicación
application = Application.builder().token(TOKEN).updater(None).build()

# Filtro de IP mejorado
@app.before_request
def verify_ip():
    client_ip = ipaddress.ip_address(request.remote_addr)
    if not any(client_ip in net for net in ALLOWED_IPS):
        logger.warning(f"Acceso denegado desde IP: {client_ip}")
        return "IP no autorizada", 403

# Health Check especial para Render
@app.route('/')
def health_check():
    return f"{BotMeta.NAME} ✅", 200

# Webhook optimizado
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        
        async def process_update():
            await application.update_queue.put(update)
            logger.info(f"Procesado update {update.update_id}")
            return "OK", 200
            
        response, status = asyncio.run(process_update())
        return Response(response, status=status)

    except Exception as e:
        logger.error(f"Error en webhook: {str(e)}")
        return "Error", 500

if __name__ == '__main__':
    from src.handlers import setup_base_handlers
    from src.handlers.crypto import precio_cripto
    from src.handlers.post import PostHandler
    from src.handlers.resume import ResumeHandler
    
    # Configuración de handlers
    post_handler = PostHandler()
    resume_handler = ResumeHandler()
    
    def setup_handlers():
        setup_base_handlers(application)
        application.add_handler(CommandHandler("precio", precio_cripto))
        application.add_handler(CommandHandler("post", post_handler.handle))
        application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
        application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
        application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))
    
    setup_handlers()
    
    # Configura comandos y webhook
    async def startup():
        await application.bot.set_my_commands([
            BotCommand("start", "Inicia el bot"),
            BotCommand("precio", "Precio de criptos"),
            BotCommand("post", "Crear post"),
            BotCommand("resumen_texto", "Resumir texto (IA)"),
            BotCommand("resumen_url", "Resumir URL (IA)")
        ])
        await application.start_webhook(
            listen="0.0.0.0",
            port=int(PORT),
            webhook_url=f"https://el-bot-de-soon.onrender.com/webhook",
            drop_pending_updates=True
        )
        await application.idle()
    
    asyncio.run(startup())
