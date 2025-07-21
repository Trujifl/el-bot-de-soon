from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from src.services.coingecko import CoinGeckoAPI  
from src.services.crypto_mapper import crypto_mapper  
from src.config import logger

async def send_crypto_price(update: Update, datos: dict):
    """Envía el precio formateado al usuario"""
    if datos.get('precio', None) == 0.00:
        await update.message.reply_text(
            "⚠️ El precio muestra $0.00. Esto puede deberse a:\n"
            "1. La criptomoneda no tiene valor en el mercado\n"
            "2. Problema temporal con la API\n"
            "3. La criptomoneda no existe",
            parse_mode="Markdown"
        )
        return

    emoji_trend = "📈" if datos.get('cambio_24h', 0) >= 0 else "📉"
    respuesta = (
        f"🔹 *{datos.get('nombre', 'Unknown')} ({datos.get('simbolo', '??').upper()})*\n"
        f"💵 Precio: ${datos.get('precio', 0):,.2f} USD\n"
        f"{emoji_trend} 24h: {datos.get('cambio_24h', 0):+.2f}%\n"
        f"🔄 Actualizado: {datos.get('ultima_actualizacion', 'N/A')}"
    )
    await update.message.reply_text(respuesta, parse_mode="Markdown")

async def show_help(update: Update):
    """Muestra ayuda para el comando /precio"""
    help_msg = (
        "💰 *Cómo usar el comando /precio*\n\n"
        "Ejemplos:\n"
        "/precio bitcoin\n"
        "/precio ETH\n"
        "/precio sol\n\n"
        "Puedes usar nombres completos o símbolos de criptomonedas.\n"
        "El bot reconoce miles de criptomonedas gracias a CoinGecko API."
    )
    await update.message.reply_text(help_msg, parse_mode="Markdown")

async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler mejorado para el comando /precio"""
    try:
        if not context.args:
            await show_help(update)
            return

        user_input = context.args[0].strip()
        logger.info(f"Consulta de precio para: {user_input}")

        await crypto_mapper.maybe_refresh_list()
        
        cripto_id = crypto_mapper.find_coin(user_input)
        
        if not cripto_id:
            suggestions = crypto_mapper.get_suggestions(user_input)
            suggestions_str = "\n".join([f"/precio {s}" for s in suggestions])
            
            await update.message.reply_text(
                f"🔍 No encontré '{user_input}'. Prueba con:\n{suggestions_str}\n\n"
                "💡 También puedes usar símbolos como ETH, BTC, SOL",
                parse_mode="Markdown"
            )
            return
            
        try:
            datos = CoinGeckoAPI.obtener_precio(cripto_id)
            if not datos:
                raise ValueError("Datos no recibidos")
                
            await send_crypto_price(update, datos)
            
        except Exception as e:
            logger.error(f"Error al obtener precio para {cripto_id}: {e}")
            await update.message.reply_text(
                "⚠️ Error al consultar el precio. Intenta nuevamente más tarde.",
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"Error en precio_cripto: {e}")
        await show_help(update)

def setup(application):
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, detectar_pregunta))

TRIGGERS = ["cuánto vale", "precio de", "valor de", "cuánto cuesta", "cotiza"]

async def detectar_pregunta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()

    for trigger in TRIGGERS:
        if trigger in texto:
            partes = texto.split(trigger)
            if len(partes) > 1:
                consulta = partes[1].strip().split()[0]
                if not consulta:
                    return
                try:
                    await crypto_mapper.maybe_refresh_list()
                    cripto_id = crypto_mapper.find_coin(consulta)
                    if not cripto_id:
                        await update.message.reply_text(f"❌ No reconocí la cripto '{consulta}'")
                        return
                    datos = CoinGeckoAPI.obtener_precio(cripto_id)
                    await send_crypto_price(update, datos)
                except Exception as e:
                    await update.message.reply_text(f"⚠️ Error: {str(e)}")
                return
