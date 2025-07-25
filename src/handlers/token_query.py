import logging
from telegram import Update, Message
from telegram.ext import ContextTypes
from src.services.crypto_mapper import CryptoMapper
from src.services.coingecko import CoinGeckoAPI
from src.services.coinmarketcap import get_price_cmc
from src.services.price_opinion import generar_respuesta_ia

logger = logging.getLogger(__name__)
crypto_mapper = CryptoMapper()

GROUP_ID = -1002348706229
TOPIC_ID = 8183

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message.chat.id == GROUP_ID and message.message_thread_id == TOPIC_ID:
        await message.reply_text("✅ ¡Hola! Estoy activo en este hilo y listo para ayudarte 🚀")

async def handle_consulta_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.effective_message
    logger.info(f"📨 Mensaje recibido: '{message.text}' de @{message.from_user.username} en {message.chat.id}/{message.message_thread_id}")

    if message.chat.id != GROUP_ID or message.message_thread_id != TOPIC_ID:
        return

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
            data = get_price_cmc(token_id)

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
