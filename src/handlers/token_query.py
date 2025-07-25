import logging
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from src.services.crypto_mapper import CryptoMapper
from src.services.coingecko import get_price_coingecko
from src.services.coinmarketcap import get_price_cmc
from src.services.price_opinion import generar_respuesta_ia

logger = logging.getLogger(__name__)
crypto_mapper = CryptoMapper()

async def handle_token_query(message: types.Message):
    logger.info(f"📨 Mensaje recibido: '{message.text}' de @{message.from_user.username} en {message.chat.id}/{message.message_thread_id}")
    
    if message.chat.id != GROUP_ID or message.message_thread_id != TOPIC_ID:
        return

    token_ids = crypto_mapper.extraer_tokens_mencionados(message.text)
    if not token_ids:
        respuesta = await generar_respuesta_ia(message.text)
        await message.reply(respuesta)
        return

    respuestas = []
    for token_id in token_ids:
        data = get_price_coingecko(token_id)
        if not data:
            data = get_price_cmc(token_id)
        if data:
            nombre = data.get("name")
            precio = data.get("price")
            symbol = data.get("symbol")
            respuesta = f"💰 {nombre} ({symbol}): ${precio}"
        else:
            respuesta = f"No pude obtener el precio de {token_id}."
        respuestas.append(respuesta)

    texto = "\n".join(respuestas)
    opinion = await generar_respuesta_ia(message.text)
    await message.reply(f"{texto}\n\n{opinion}")
