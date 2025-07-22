from telegram import Update
from telegram.ext import ContextTypes
from src.services.crypto_mapper import crypto_mapper
from src.services.coingecko import CoinGeckoAPI
from src.services.coinmarketcap import CoinMarketCapAPI  
from src.services.price_updater import get_precio_desde_cache
from src.config import logger
from src.services.price_opinion import construir_contexto_opinion, armar_prompt_opinion
from src.services.openai import generar_respuesta_ia

async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text(
                "💰 Usa `/precio <token>` para consultar, por ejemplo:\n"
                "`/precio btc`, `/precio ethereum`, `/precio sol`",
                parse_mode="Markdown"
            )
            return

        user_input = context.args[0].strip()
        logger.info(f"Consulta de precio para: {user_input}")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        await crypto_mapper.maybe_refresh_list()
        cripto_id = crypto_mapper.find_coin(user_input)

       
        datos = get_precio_desde_cache(cripto_id) if cripto_id else None

        # 2️⃣ 
        if not datos and cripto_id:
            datos = CoinGeckoAPI.obtener_precio(cripto_id)

        # 3️⃣ 
        if not datos:
            datos = CoinMarketCapAPI.obtener_precio(user_input)

        if not datos:
            await update.message.reply_text(
                f"❌ No pude obtener el precio de '{user_input.upper()}'. Asegúrate de que sea un token válido."
            )
            return

        emoji_trend = "📈" if datos.get('cambio_24h', 0) >= 0 else "📉"
        respuesta = (
            f"🔹 *{datos.get('nombre', 'Unknown')} ({datos.get('symbol', '??').upper()})*\n"
            f"💵 Precio: ${datos.get('precio', 0):,.2f} USD\n"
            f"{emoji_trend} 24h: {datos.get('cambio_24h', 0):+.2f}%"
        )
        await update.message.reply_text(respuesta, parse_mode="Markdown")

       
        contexto = construir_contexto_opinion(datos)
        prompt = armar_prompt_opinion(datos)
        disclaimer = (
            "\n\n⚠️ *Aviso rápido:* Este análisis es solo informativo y con un toque de humor. "
            "¡No tomes decisiones de inversión solo por lo que diga un bot! 😉"
        )
        respuesta_ia = await generar_respuesta_ia(prompt, update.effective_user.first_name, contexto)
        await update.message.reply_text(respuesta_ia + disclaimer, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error en /precio: {e}")
        await update.message.reply_text("⚠️ Error al consultar el precio. Intenta nuevamente más tarde.")
