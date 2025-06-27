#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BOT DE TELEGRAM CON RESÚMENES Y COINGECKO API - VERSIÓN 24/7 PARA RENDER
"""

import os
import sys
import logging
import random
import requests
import threading
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, jsonify

# Configuración básica de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración de Flask para el health check
app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "bot": "active"}), 200

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "bot": "SoonBot",
        "version": "8.4"
    }), 200

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv no está instalado, usando variables de entorno del sistema")

# Importaciones de Telegram
try:
    from telegram import (
        Update,
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        Bot
    )
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        filters,
        ContextTypes
    )
    
    # Importaciones de IA (opcional)
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    logger.error("Instala las dependencias con: pip install python-telegram-bot openai python-dotenv requests beautifulsoup4 flask")
    sys.exit(1)

# Configuración del bot
TOKEN = os.getenv("TELEGRAM_TOKEN")
COINGECKO_API = "https://api.coingecko.com/api/v3"
ADMIN_IDS = [int(id) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id]
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
if not TOKEN:
    logger.error("TELEGRAM_TOKEN no está configurado")
    sys.exit(1)

# Configuración para Render
RENDER = os.getenv("RENDER", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))  # Render usa el puerto 10000 por defecto

# Personalidad del bot
BOT_PERSONALITY = {
    "nombre": "SoonBot",
    "emoji": "🚀",
    "version": "8.4",
    "tono": "pro-latino-relajado",
    "criptos_comunes": ["bitcoin", "ethereum", "binancecoin", "solana", "cardano", "ripple", "dogecoin"],
    "frases": {
        "saludos": [
            "¡Epa {nombre}! ¿como anda, todo bien? 👊", 
            "¡Buenaas {nombre}! ¿En qué te ayudo? 🔥",
            "¡Buenas crack! Dime cómo colaboramos hoy 💼",
            "¡Waaasaa {nombre}! Listo para lo que necesites ⚡"
        ],
        "despedidas": [
            "¡Listo socio! Cualquier cosa me chiflas 👌",
            "Nos vemos {nombre}, no te quedas ghosteando 👻",
            "Hasta luego, ¡que no se te caiga el exchange! 😎",
            "Chao pescao, éxito en esas inversiones 🐟"
        ],
        "positivas": [
            "¡Juega vivo! Así me gusta 😏",
            "¡Esooo Excelente! Apretaste el botón correcto 🤙",
            "¡Confirmado! Más rápido que transacción en Solana ⚡",
            "¡Listo! Más fácil que minar con ASIC ✅"
        ],
        "error": [
            "¡Chale {nombre}! Algo se bugueó 😅 ¿Le damos F5?",
            "Error 404 - Aquí no hay crypto... pero reintentemos 🔄",
            "Se cayó como LUNA... pero ya lo reseteamos 🌕",
            "¡Ups! Parece que me doxxearon... broma, reintenta 👀"
        ],
        "espera": [
            "Tranqui, no es rugpull... procesando 🕵️",
            "Espera espera, como en ICO... cargando 📈",
            "Mándame un memecoin mientras esperas... trabajando 🐶",
            "Más rápido que Binance en caída... pero dame un toque ⏳"
        ]
    },
    "caracteristicas": {
        "tono": "Serio técnico pero con humor crypto",
        "modismos": ["crack", "socio", "wey", "juega vivo"],
        "humor": "Referencias crypto + ironía ligera",
        "emoji_usage": "Estratégico (1-2 por mensaje)"
    }
}

# Diccionario global para almacenar posts pendientes
PENDING_POSTS: Dict[int, Dict] = {}

# Sistema de keep-alive para Render
def keep_alive():
    while True:
        try:
            if RENDER and WEBHOOK_URL:
                requests.get(f"{WEBHOOK_URL}/health")
                logger.info("Keep-alive ping enviado")
        except Exception as e:
            logger.warning(f"Error en keep-alive: {e}")
        time.sleep(300)  # Ping cada 5 minutos (300 segundos)

if RENDER:
    threading.Thread(target=keep_alive, daemon=True).start()

class CoinGeckoAPI:
    @staticmethod
    def obtener_precio(cripto_id: str) -> Optional[Dict]:
        """Obtiene precio actual desde CoinGecko"""
        try:
            cripto_id = cripto_id.lower()
            endpoint = f"{COINGECKO_API}/coins/{cripto_id}"
            params = {
                "tickers": False,
                "market_data": True,
                "community_data": False,
                "developer_data": False
            }
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "nombre": data["name"],
                "simbolo": data["symbol"].upper(),
                "precio": data["market_data"]["current_price"]["usd"],
                "cambio_24h": data["market_data"]["price_change_percentage_24h"],
                "max_24h": data["market_data"]["high_24h"]["usd"],
                "min_24h": data["market_data"]["low_24h"]["usd"]
            }
        except Exception as e:
            logger.error(f"Error en CoinGecko API: {e}")
            return None

    @staticmethod
    def buscar_cripto(query: str) -> Optional[str]:
        """Busca el ID correcto de una criptomoneda"""
        try:
            response = requests.get(f"{COINGECKO_API}/search?query={query}", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data["coins"][0]["id"] if data["coins"] else None
        except Exception as e:
            logger.error(f"Error al buscar cripto: {e}")
            return None

class PersonalidadBot:
    @staticmethod
    def generar_respuesta(prompt: str, user_name: str = None) -> str:
        """Genera una respuesta con la personalidad del bot"""
        frases = BOT_PERSONALITY["frases"]
        
        if "hola" in prompt.lower():
            saludo = random.choice(frases["saludos"])
            return saludo.format(nombre=user_name) if user_name else saludo
        
        if "gracias" in prompt.lower():
            return random.choice([
                f"¡De nada {user_name}! 😊" if user_name else "¡De nada! 😊",
                "¡Con gusto! 👍",
                "¡Para eso estoy! ✨"
            ])
        
        return None

    @staticmethod
    async def generar_respuesta_ia(prompt: str, user_name: str = None) -> str:
        """Genera respuesta usando OpenAI (opcional)"""
        if not os.getenv("OPENAI_API_KEY"):
            return None
            
        try:
            personalizacion = f"El usuario se llama {user_name}. " if user_name else ""
            prompt_completo = (
                f"{BOT_PERSONALITY['tono']} {personalizacion}"
                f"El usuario pregunta: '{prompt}'. Responde de manera profesional pero cercana:"
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": BOT_PERSONALITY['tono']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error en OpenAI: {e}")
            return None

class PostManager:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.pending_posts = PENDING_POSTS
    
    async def enviar_vista_previa(self, user_id: int, post_data: Dict) -> int:
        """Envía vista previa del post al usuario"""
        preview_text = (
            f"📋 <b>VISTA PREVIA DEL POST</b>\n\n"
            f"<b>Título:</b> {post_data['titulo']}\n"
            f"<b>Contenido:</b>\n{post_data['contenido']}\n\n"
            f"ℹ️ Este post está pendiente de aprobación"
        )
        
        message = await self.bot.send_message(
            chat_id=user_id,
            text=preview_text,
            parse_mode="HTML"
        )
        return message.message_id
    
    async def solicitar_aprobacion(self, post_data: Dict):
        """Envía solicitud de aprobación a los administradores"""
        approval_text = (
            f"🛎️ <b>SOLICITUD DE APROBACIÓN DE POST</b>\n\n"
            f"👤 <b>Usuario:</b> {post_data['user_name']}\n"
            f"📢 <b>Título:</b> {post_data['titulo']}\n\n"
            f"📝 <b>Contenido:</b>\n{post_data['contenido']}\n\n"
            f"🆔 <code>Post ID: {post_data['post_id']}</code>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Aprobar", callback_data=f"approve_{post_data['post_id']}"),
                InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{post_data['post_id']}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        for admin_id in ADMIN_IDS:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=approval_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error al enviar aprobación a admin {admin_id}: {e}")
    
    async def publicar_en_canal(self, post_data: Dict) -> bool:
        """Publica el post en el canal"""
        if not CHANNEL_ID:
            logger.error("No se configuró CHANNEL_ID")
            return False
        
        post_text = (
            f"📢 <b>{post_data['titulo']}</b> {BOT_PERSONALITY['emoji']}\n\n"
            f"{post_data['contenido']}\n\n"
            f"#Cripto #Análisis"
        )
        
        try:
            await self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=post_text,
                parse_mode="HTML"
            )
            return True
        except Exception as e:
            logger.error(f"Error al publicar en el canal: {e}")
            return False

class ResumenManager:
    @staticmethod
    async def generar_resumen_ia(texto: str, es_url: bool = False) -> str:
        """Genera resumen usando IA (traducido al español)"""
        try:
            if es_url:
                # Extraer contenido de la página web
                response = requests.get(texto, timeout=10)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                contenido = ' '.join([p.get_text() for p in soup.find_all('p')])
                prompt = f"Resume este artículo en 3 párrafos en español (traduce si es necesario):\n{contenido[:3000]}"
            else:
                prompt = f"Resume este texto en 3 párrafos en español (traduce si es necesario):\n{texto[:3000]}"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente que resume y traduce contenido al español."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return None

# Instancias globales
persona = PersonalidadBot()
post_manager = PostManager()
coingecko = CoinGeckoAPI()
resumen_manager = ResumenManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador del comando /start"""
    try:
        user_name = update.effective_user.first_name
        saludo = random.choice(BOT_PERSONALITY["frases"]["saludos"]).format(nombre=user_name)
        
        respuesta = (
            f"{saludo}\n\n"
            "Soy tu asistente de criptomonedas. Puedo ayudarte con:\n\n"
            "💹 <b>Precios de Criptomonedas</b>\n"
            "/precio [nombre] - Muestra datos actuales\n\n"
            "📢 <b>Publicaciones</b>\n"
            "/post - Crear contenido para el canal\n\n"
            "📝 <b>Resúmenes</b>\n"
            "/resumen_texto - Resume texto en español\n"
            "/resumen_url - Resume páginas web\n\n"
            "💡 También puedes preguntarme directamente en el chat."
        )
        
        await update.message.reply_text(respuesta, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error en start: {e}")
        await update.message.reply_text(random.choice(BOT_PERSONALITY["frases"]["error"]))

async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para el comando /precio"""
    try:
        user_name = update.effective_user.first_name
        query = " ".join(context.args).lower() if context.args else "bitcoin"
        
        await update.message.reply_chat_action(action="typing")
        cripto_id = coingecko.buscar_cripto(query)
        
        if not cripto_id:
            await update.message.reply_text(
                f"⚠️ No encontré '{query}'. Prueba con el nombre técnico (ej: 'ethereum' en lugar de 'ether')",
                parse_mode="HTML"
            )
            return
        
        datos = coingecko.obtener_precio(cripto_id)
        if not datos:
            raise Exception("No se pudieron obtener los datos")
        
        # Formatear respuesta
        cambio_emoji = "📈" if datos["cambio_24h"] >= 0 else "📉"
        respuesta = (
            f"💹 <b>{datos['nombre']} ({datos['simbolo']})</b>\n\n"
            f"🪙 <b>Precio:</b> ${datos['precio']:,.2f} USD\n"
            f"{cambio_emoji} <b>24h:</b> {datos['cambio_24h']:+.2f}%\n"
            f"🔺 <b>Máx 24h:</b> ${datos['max_24h']:,.2f}\n"
            f"🔻 <b>Mín 24h:</b> ${datos['min_24h']:,.2f}\n\n"
            f"ℹ️ Datos en tiempo real via CoinGecko"
        )
        
        await update.message.reply_text(respuesta, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error en precio_cripto: {e}")
        await update.message.reply_text(random.choice(BOT_PERSONALITY["frases"]["error"]))

async def post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para crear posts"""
    try:
        user_name = update.effective_user.first_name
        
        if not context.args:
            respuesta = (
                f"¡Hola {user_name}! Vamos a crear un post para el canal. {BOT_PERSONALITY['emoji']}\n\n"
                "<b>Cómo se usa:</b>\n"
                "<code>/post [Título] | [Contenido]</code>\n\n"
                "Ejemplo:\n"
                "<code>/post Bitcoin en alza | El BTC supera los $65k con un aumento del 5%...</code>"
            )
            await update.message.reply_text(respuesta, parse_mode="HTML")
            return
            
        texto = " ".join(context.args)
        if "|" not in texto:
            await update.message.reply_text(
                f"¡Ups {user_name}! Falta el separador |\n"
                "El formato correcto es: /post [Título] | [Contenido]"
            )
            return
            
        titulo, contenido = texto.split("|", 1)
        post_id = hash(f"{titulo}{contenido}{datetime.now().timestamp()}")
        
        # Almacenar post pendiente
        PENDING_POSTS[post_id] = {
            "post_id": post_id,
            "titulo": titulo.strip(),
            "contenido": contenido.strip(),
            "user_id": update.effective_user.id,
            "user_name": user_name,
            "status": "pending"
        }
        
        # Enviar vista previa y solicitar aprobación
        await post_manager.enviar_vista_previa(update.effective_user.id, PENDING_POSTS[post_id])
        await post_manager.solicitar_aprobacion(PENDING_POSTS[post_id])
        
        await update.message.reply_text(
            f"✅ ¡Listo {user_name}! Tu post está en revisión.\n"
            "Te avisaré cuando sea aprobado."
        )
        
    except Exception as e:
        logger.error(f"Error en post_handler: {e}")
        await update.message.reply_text(random.choice(BOT_PERSONALITY["frases"]["error"]))

async def resumen_texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resume texto proporcionado por el usuario"""
    try:
        user_name = update.effective_user.first_name
        texto = ' '.join(context.args) if context.args else None
        
        if not texto:
            await update.message.reply_text(
                "📝 <b>Uso:</b> <code>/resumen_texto [texto a resumir]</code>\n\n"
                "Ejemplo:\n"
                "<code>/resumen_texto Bitcoin es una criptomoneda descentralizada inventada en 2008...</code>",
                parse_mode="HTML"
            )
            return

        await update.message.reply_chat_action(action="typing")
        
        if os.getenv("OPENAI_API_KEY"):
            resumen = await resumen_manager.generar_resumen_ia(texto)
            if resumen:
                await update.message.reply_text(
                    f"📚 <b>Resumen:</b>\n\n{resumen}",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("⚠️ No pude generar el resumen. Intenta más tarde.")
        else:
            await update.message.reply_text(
                "ℹ️ La función de resumen requiere configuración de OpenAI API.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error en resumen_texto: {e}")
        await update.message.reply_text(random.choice(BOT_PERSONALITY["frases"]["error"]))

async def resumen_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resume el contenido de una página web"""
    try:
        user_name = update.effective_user.first_name
        url = ' '.join(context.args) if context.args else None
        
        if not url:
            await update.message.reply_text(
                "🌐 <b>Uso:</b> <code>/resumen_url [URL]</code>\n\n"
                "Ejemplo:\n"
                "<code>/resumen_url https://es.wikipedia.org/wiki/Bitcoin</code>",
                parse_mode="HTML"
            )
            return

        # Validar URL
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            await update.message.reply_text("⚠️ Por favor ingresa una URL válida (ej: https://ejemplo.com)")
            return

        await update.message.reply_chat_action(action="typing")
        
        if os.getenv("OPENAI_API_KEY"):
            resumen = await resumen_manager.generar_resumen_ia(url, es_url=True)
            if resumen:
                await update.message.reply_text(
                    f"🌐 <b>Resumen de {url}</b>\n\n{resumen}",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("⚠️ No pude generar el resumen. Intenta con otra URL.")
        else:
            await update.message.reply_text(
                "ℹ️ La función de resumen requiere configuración de OpenAI API.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error en resumen_url: {e}")
        await update.message.reply_text(random.choice(BOT_PERSONALITY["frases"]["error"]))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para interacciones con botones"""
    query = update.callback_query
    await query.answer()
    
    try:
        action, post_id = query.data.split("_")
        post_id = int(post_id)
        
        if post_id not in PENDING_POSTS:
            await query.edit_message_text("⚠️ Este post ya fue procesado")
            return
            
        user_name = PENDING_POSTS[post_id]["user_name"]
        
        if action == "approve":
            success = await post_manager.publicar_en_canal(PENDING_POSTS[post_id])
            if success:
                await context.bot.send_message(
                    chat_id=PENDING_POSTS[post_id]["user_id"],
                    text=f"¡Tu post '{PENDING_POSTS[post_id]['titulo']}' ha sido aprobado y publicado! 🎉",
                    parse_mode="HTML"
                )
                await query.edit_message_text(f"✅ Post publicado por {user_name}")
                PENDING_POSTS[post_id]["status"] = "approved"
            else:
                await query.edit_message_text("⚠️ Error al publicar")
                
        elif action == "reject":
            await context.bot.send_message(
                chat_id=PENDING_POSTS[post_id]["user_id"],
                text=f"Tu post '{PENDING_POSTS[post_id]['titulo']}' no fue aprobado esta vez. "
                     "Puedes editarlo y volver a enviarlo.",
                parse_mode="HTML"
            )
            await query.edit_message_text(f"❌ Post rechazado ({user_name})")
            PENDING_POSTS[post_id]["status"] = "rejected"
            
    except Exception as e:
        logger.error(f"Error en button_handler: {e}")
        await query.edit_message_text("⚠️ Error al procesar esta acción")

async def mensaje_generico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para mensajes no comandos"""
    try:
        texto = update.message.text
        user_name = update.effective_user.first_name
        
        if len(texto) < 3 or texto.startswith('/'):
            return
        
        # Detección de criptomonedas
        cripto = await detectar_cripto(texto)
        if cripto:
            await update.message.reply_text(
                f"🔍 Veo que mencionas {cripto}. Dame un segundo...",
                reply_to_message_id=update.message.message_id
            )
            context.args = [cripto]
            await precio_cripto(update, context)
            return
        
        # Respuestas predefinidas
        respuesta_predefinida = persona.generar_respuesta(texto, user_name)
        if respuesta_predefinida:
            await update.message.reply_text(respuesta_predefinida)
            return
        
        # Respuesta con IA (opcional)
        if os.getenv("OPENAI_API_KEY"):
            await update.message.reply_chat_action(action="typing")
            respuesta_ia = await persona.generar_respuesta_ia(texto, user_name)
            if respuesta_ia:
                await update.message.reply_text(respuesta_ia)
                return
        
        # Respuesta por defecto
        await update.message.reply_text(
            f"¿Te gustaría saber el precio de alguna criptomoneda, {user_name}? "
            f"Prueba con '/precio bitcoin' o menciona alguna en tu mensaje.",
            reply_to_message_id=update.message.message_id
        )
            
    except Exception as e:
        logger.error(f"Error en mensaje_generico: {e}")
        await update.message.reply_text(random.choice(BOT_PERSONALITY["frases"]["error"]))

async def detectar_cripto(texto: str) -> Optional[str]:
    """Detecta menciones de criptomonedas comunes"""
    texto = texto.lower()
    for cripto in BOT_PERSONALITY["criptos_comunes"]:
        if cripto in texto:
            return cripto
    return None

def setup_bot() -> Application:
    """Configuración del bot"""
    app = Application.builder().token(TOKEN).build()
    
    # Handlers de comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("precio", precio_cripto))
    app.add_handler(CommandHandler("post", post_handler))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("resumen_texto", resumen_texto))
    app.add_handler(CommandHandler("resumen_url", resumen_url))
    
    # Handlers de interacción
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_generico))
    
    logger.info(f"✅ {BOT_PERSONALITY['nombre']} v{BOT_PERSONALITY['version']} listo")
    return app

def main() -> None:
    """Función principal"""
    try:
        logger.info(f"Iniciando {BOT_PERSONALITY['nombre']} v{BOT_PERSONALITY['version']}...")
        
        if RENDER:
            logger.info("Modo Render activado - Configurando webhook...")
            from threading import Thread
            from waitress import serve
            
            # Iniciar Flask en un hilo separado
            flask_thread = Thread(target=lambda: serve(app, host="0.0.0.0", port=5000))
            flask_thread.daemon = True
            flask_thread.start()
            
            # Configurar el bot de Telegram
            bot = setup_bot()
            
            async def startup():
                await bot.bot.set_webhook(
                    url=f"{WEBHOOK_URL}/{TOKEN}",
                    drop_pending_updates=True
                )
                logger.info(f"Webhook configurado en {WEBHOOK_URL}")
            
            bot.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
                startup=startup
            )
        else:
            logger.info("Modo local activado - Usando polling...")
            bot = setup_bot()
            bot.run_polling()
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()