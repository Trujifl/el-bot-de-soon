from telegram import Update
from telegram.ext import ContextTypes
from src.services.price_updater import get_precio_desde_cache
from src.services.coingecko import CoinGeckoAPI
from src.services.coinmarketcap import CoinMarketCapAPI 
from src.services.openai import generar_respuesta_ia
from src.services.crypto_mapper import crypto_mapper

async def handle_consulta_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.message.text.lower()

        posibles_monedas = await crypto_mapper.extraer_tokens_mencionados(query)
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
            emoji_trend = "📈" if datos.get('cambio_24h', 0) >= 0 else "📉"
            texto = (
                f"🔹 *{datos.get('nombre', 'Unknown')} ({datos.get('simbolo', '??').upper()})*\n"
                f"💵 Price: ${datos.get('precio', 0):,.2f} USD\n"
                f"{emoji_trend} 24h: {datos.get('cambio_24h', 0):+.2f}%\n"
                f"🕒 Updated: {datos.get('ultima_actualizacion', 'N/A')}"
            )
            await update.message.reply_text(texto, parse_mode="Markdown")

            contexto = f"Token consultado: {token}\n{texto}"
            prompt = (
                "Eres un analista de mercado cripto. Basado en los datos entregados, genera una breve "
                "explicación en español sobre la situación actual del token consultado, con un estilo claro y profesional."
            )
            opinion = await generar_respuesta_ia(prompt, update.effective_user.first_name, contexto)

            disclaimer = (
                "\n\n⚠️ *Disclaimer:* Este contenido es informativo. No representa consejo financiero. Haz tu propia investigación. 😉"
            )
            await update.message.reply_text(opinion + disclaimer, parse_mode="Markdown")
        else:
            prompt = (
                f"Eres un experto en criptomonedas. Un usuario preguntó sobre '{query}'. "
                "No se encontraron datos directos, así que responde con un resumen informativo general "
                "en español sobre el activo mencionado, su posible uso, origen o aplicación."
            )
            fallback = await generar_respuesta_ia(prompt, update.effective_user.first_name, query)
            await update.message.reply_text(fallback, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text("⚠️ Error al procesar tu consulta. Intenta más tarde.")
