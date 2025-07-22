# src/handlers/solo_topic.py

THREAD_ID_TESTEO = 42  # ⚠️ Cambia este valor cuando lo sepas

async def recibir_solo_en_topic(update, context):
    if (
        update.message
        and update.message.message_thread_id == THREAD_ID_TESTEO
    ):
        await update.message.reply_text("✅ Mensaje recibido en el topic correcto")
    else:
        print("📛 Mensaje ignorado (otro topic)")
        return
