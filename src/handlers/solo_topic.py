from src.handlers.token_query import handle_consulta_token
from src.services.openai import generar_respuesta_ia
import os
import traceback

# Leer los chat_id autorizados desde variable de entorno
ids = os.getenv("TELEGRAM_CHANNEL_ID", "")
GRUPOS_AUTORIZADOS = [int(x.strip()) for x in ids.split(",") if x.strip()]

# Leer los admin_id para uso en chat privado
admin_ids = os.getenv("TELEGRAM_ADMIN_IDS", "")
USUARIOS_ADMIN = [int(x.strip()) for x in admin_ids.split(",") if x.strip()]

async def recibir(update, context):
    if update.message is None:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    texto = update.message.text or ""

    # ⚙️ Obtener nombre de usuario del bot
    me = await context.bot.get_me()
    bot_username = me.username.lower()

    # 🧠 Revisar mención explícita o respuesta directa
    texto_original = texto or ""
    mencion_directa = any(
        ent.type == "mention" and texto_original[ent.offset:ent.offset + ent.length].lower() == f"@{bot_username}"
        for ent in update.message.entities or []
    )

    respuesta_al_bot = (
        update.message.reply_to_message
        and update.message.reply_to_message.from_user
        and update.message.reply_to_message.from_user.id == me.id
    )

    if chat_type in ["group", "supergroup"]:
        if chat_id not in GRUPOS_AUTORIZADOS:
            print(f"⛔ Grupo no autorizado: {chat_id}")
            return
        if not (mencion_directa or respuesta_al_bot):
            print(f"🤐 Ignorado: sin mención ni respuesta directa al bot en {chat_id}")
            return

    elif chat_type == "private":
        if user_id not in USUARIOS_ADMIN:
            print(f"⛔ Usuario no autorizado en privado: {user_id}")
            return

    print(f"✅ Mensaje aceptado de chat {chat_id} por usuario {user_id}")

    try:
        user_msg = texto
        user_name = update.effective_user.first_name
        contexto = {}

        respuesta = await generar_respuesta_ia(user_msg, user_name, contexto)
        await update.message.reply_text(respuesta)

    except Exception as e:
        print(f"❌ Error en IA: {e}")
        traceback.print_exc()
        await update.message.reply_text("⚠️ Error al procesar tu consulta. Intenta más tarde.")
