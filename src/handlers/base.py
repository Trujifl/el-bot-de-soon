from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from src.config import logger
from src.services.openai import generar_respuesta_ia
from src.services.coingecko import CoinGeckoAPI
from src.utils.personality import Personalidad
from src.utils.filters import MentionedBotFilter, TopicFilter

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
    # Verificación directa por texto, ignorando si no comienza con @
    if not update.message or not update.message.text:
        return

    bot_username = (await context.bot.get_me()).username.lower()
    if not update.message.text.strip().lower().startswith(f"@{bot_username}"):
        return

    user_msg = update.message.text.lower()
    user_name = update.effective_user.first_name
    ctx = context.chat_data.get("cripto_ctx", {})

    if any(p in user_msg for p in ["precio", "a cuánto", "valor de"]):
        cripto = next((c for c in ["btc", "eth", "sol", "bitcoin", "ethereum", "solana"] 
                      if c in user_msg), None)

        if cripto:
            try:
                cripto_id = "bitcoin" if cripto in ["btc", "bitcoin"] else \
                            "ethereum" if cripto in ["eth", "ethereum"] else \
                            "solana" if cripto in ["sol", "solana"] else cripto

                datos = CoinGeckoAPI.obtener_precio(cripto_id)
                ctx[cripto] = datos
                opinion = Personalidad.generar_opinion_cripto(cripto_id, datos)

                respuesta = (
                    f"📊 {datos['nombre']} ({datos['simbolo'].upper()})\n"
                    f"💵 Precio: ${datos['precio']:,.2f}\n"
                    f"📈 24h: {datos['cambio_24h']:+.2f}%\n\n"
                    f"{opinion}"
                )

            except Exception as e:
                logger.error(f"Error al obtener precio: {str(e)}")
                respuesta = Personalidad.generar_respuesta_error(user_name)

            await update.message.reply_text(respuesta)
            return

    try:
        respuesta = await generar_respuesta_ia(user_msg, user_name, ctx)
        await update.message.reply_text(respuesta)
    except Exception as e:
        logger.error(f"Error en IA: {str(e)}")
        await update.message.reply_text(Personalidad.generar_respuesta_error(user_name))

def setup_base_handlers(application):
    filtro = MentionedBotFilter() & TopicFilter()
    application.add_handler(CommandHandler("start", start, filters=filtro))
    application.add_handler(CommandHandler("help", help_command, filters=filtro))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filtro, handle_message))
