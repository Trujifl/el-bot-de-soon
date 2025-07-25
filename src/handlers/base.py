from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from src.services.openai import generar_respuesta_ia
from src.utils.personality import Personalidad

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    saludo = Personalidad.get_random_saludo(user.first_name)
    await update.message.reply_text(
        f"{saludo}\n\nSoy SoonBot, tu asistente experto en criptomonedas.",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ *Comandos disponibles:*\n\n"
        "*/start* - Mensaje de bienvenida\n"
        "*/precio [cripto]* - Consultar precios (ej: /precio BTC)\n"
        "*/resumen* - Resumir contenido (texto o URL)\n"
        "*/post* - Crear publicación para el canal\n\n"
        "📌 *Uso específico:*\n"
        "Escribe solo el comando para ver instrucciones detalladas"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    user_name = update.effective_user.first_name

    if any(p in user_msg for p in ["precio", "a cuánto", "cuánto vale", "valor de"]):
        await update.message.reply_text(
            f"Hola {user_name}, para consultar el precio de una cripto escribe `/precio BTC`, por ejemplo.",
            parse_mode="Markdown"
        )
        return

    respuesta = generar_respuesta_ia(user_msg)
    await update.message.reply_text(respuesta)

async def handle_comando_general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    if "/start" in text:
        await start(update, context)
    elif "/help" in text:
        await help_command(update, context)
    elif "/precio" in text:
        await update.message.reply_text("💰 Usa `/precio BTC` para consultar el precio.")
    elif "/resumen" in text:
        await update.message.reply_text("📄 Usa `/resumen_url` o `/resumen_texto` para resumir contenido.")
    elif "/post" in text:
        await update.message.reply_text("📢 Has invocado `/post`. Este comando requiere permisos especiales.")
    else:
        respuesta = generar_respuesta_ia(text)
        await update.message.reply_text(respuesta)

def setup_base_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.COMMAND, handle_comando_general))
