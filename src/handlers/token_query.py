from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from src.services.price_updater import get_precio_desde_cache
from src.services.coingecko import CoinGeckoAPI
from src.services.coinmarketcap import CoinMarketCapAPI
from src.services.openai import generar_respuesta_ia
from src.services.crypto_mapper import crypto_mapper
from src.utils.filters import MentionedBotFilter
from src.config import logger


async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Debes indicar un token. Ejemplo: /precio BTC")
        return

    token = context.args[0].upper()
    resultado = CoinGeckoAPI.obtener_precio(token) or CoinMarketCapAPI.obtener_precio(token)

    if resultado and "precio" in resultado:
        nombre = resultado.get("nombre", token.upper())
        precio = resultado["precio"]
        cambio = resultado.get("cambio_24h", 0)
        tendencia = "📈" if cambio >= 0 else "📉"

        await update.message.reply_text(
            f"💰 *{nombre}*\n"
            f"Precio actual: *${precio}*\n"
            f"Cambio 24h: *{cambio}%*",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"No pude obtener el precio de {token}.")


async def handle_consulta_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.message.text.lower()
        posibles_monedas = crypto_mapper.extraer_tokens_mencionados(query)

        if not posibles_monedas:
            await update.message.reply_text("❌ No identifiqué una criptomoneda en tu mensaje.")
            return

        token = posibles_monedas[0]
        cripto_id = crypto_mapper.find_coin(token)

        datos = get_precio_desde_cache(cripto_id) if cripto_id else None
        if not datos and cripto_id:
            datos = CoinGeckoAPI.obtener_precio(cripto_id)

        if not datos:
            datos = CoinMarketCapAPI.obtener_precio(token)

        if datos:
            nombre = datos.get('nombre', token.capitalize())
            simbolo = datos.get('symbol') or datos.get('simbolo') or token.upper()
            precio = datos.get('precio', 0)
            cambio = datos.get('cambio_24h', 0)
            tendencia = "📈" if cambio >= 0 else "📉"

            texto = (
                f"🔹 *{nombre} ({simbolo})*\n"
                f"💵 Precio: ${precio:.4f}\n"
                f"{tendencia} Cambio 24h: {cambio:.2f}%"
            )
            await update.message.reply_text(texto, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ No pude obtener el precio actual.")
    except Exception as e:
        logger.exception("Error procesando consulta token")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar tu consulta.")


def setup_token_query_handler(application):
    # /precio BTC
    application.add_handler(CommandHandler("precio", precio_cripto))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & MentionedBotFilter(),
        handle_consulta_token
    ))
