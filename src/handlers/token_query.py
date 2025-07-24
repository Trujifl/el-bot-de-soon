from telegram import Update
from telegram.ext import ContextTypes
from src.services.price_updater import get_precio_desde_cache
from src.services.coingecko import CoinGeckoAPI
from src.services.coinmarketcap import CoinMarketCapAPI
from src.services.openai import generar_respuesta_ia
from src.services.crypto_mapper import crypto_mapper
from src.config import logger


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
