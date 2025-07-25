import logging
from telegram import Update, Message
from telegram.ext import ContextTypes
from src.services.crypto_mapper import CryptoMapper
from src.services.coingecko import CoinGeckoAPI
from src.services.coinmarketcap import obtener_precio_desde_coinmarketcap
from src.services.price_opinion import generar_respuesta_ia

logger = logging.getLogger(__name__)
crypto_mapper = CryptoMapper()

async def handle_consulta_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.effective_message
    logger.info(f"📨 Mensaje recibido: '{message.text}' de @{message.from_user.username} en {message.chat.id}")

    token_ids = crypto_mapper.extraer_tokens_mencionados(message.text)
    if not token_ids:
        respuesta = await generar_respuesta_ia(message.text)
        await message.reply_text(respuesta)
        return

    respuestas = []
    for token_id in token_ids:
        try:
            data = CoinGeckoAPI.obtener_precio(token_id)
        except Exception:
            data = obtener_precio_desde_coinmarketcap(token_id)

        if data:
            nombre = data.get("nombre")
            precio = data.get("precio")
            simbolo = data.get("simbolo")
            respuesta = f"💰 {nombre} ({simbolo}): ${precio}"
        else:
            respuesta = f"No pude obtener el precio de {token_id}."

        respuestas.append(respuesta)

    texto = "\n".join(respuestas)
    opinion = await generar_respuesta_ia(message.text)
    await message.reply_text(f"{texto}\n\n{opinion}")
