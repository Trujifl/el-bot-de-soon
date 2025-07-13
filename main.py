import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackQueryHandler
from telegram import BotCommand
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    PORT,
    WEBHOOK_URL,
    RENDER,
    logger,
    BotMeta,
    BotPersonality
)
from src.handlers.base import start, help_command, mensaje_generico, setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler

post_handler = PostHandler()
resume_handler = ResumeHandler()



async def set_bot_commands(application):
    """Configura los comandos visibles en la interfaz de Telegram"""
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("help", "Muestra ayuda"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto en español"),
        BotCommand("resumen_url", "Resume una página web en español")
    ]
    await application.bot.set_my_commands(commands)

def main():
    try:
        # 1. Inicialización del bot
        application = Application.builder().token(TOKEN).build()
        
        # 2. Configuración de handlers
        setup_base_handlers(application)
        application.add_handler(CommandHandler("precio", precio_cripto))
        application.add_handler(CommandHandler("post", post_handler.handle))
        application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
        application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
        application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))
        
        # 3. Configurar comandos visibles
        application.post_init = set_bot_commands
        
        logger.info(f"[{BotMeta.NAME} v{BotMeta.VERSION} iniciando...]")
        
        # 4. Modo de ejecución
        if RENDER:
            logger.info("Modo Render - Configurando webhook...")
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
                secret_token=os.getenv("WEBHOOK_SECRET", "SECRET_TOKEN")
            )
        else:
            logger.info("Modo local - Usando polling...")
            application.run_polling()
            
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")
        raise

if __name__ == "__main__":
    main()