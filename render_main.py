from flask import Flask, request, Response
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import asyncio
import logging
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

app = Flask(__name__)
post_handler = PostHandler()
resume_handler = ResumeHandler()

# Configuración de la aplicación con el token del bot
application = Application.builder().token(TOKEN).updater(None).build()

async def set_commands():
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto con IA"),
        BotCommand("resumen_url", "Resume una página web con IA")
    ]
    await application.bot.set_my_commands(commands)

def setup_handlers():
    setup_base_handlers(application)
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("post", post_handler.handle))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Verificación implícita mediante el token en la URL
        update = Update.de_json(request.json, application.bot)
        
        async def process_update():
            await application.update_queue.put(update)
            logger.info(f"[{BotMeta.NAME}] Mensaje procesado")
            return "OK", 200
            
        return Response(
            asyncio.run(process_update()),
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} activo ✅", 200

if __name__ == '__main__':
    setup_handlers()
    set_commands()  # Configura los comandos al iniciar
    
    application.run_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        webhook_url=f"https://el-bot-de-soon.onrender.com/webhook?token={TOKEN}",
        drop_pending_updates=True
    )
