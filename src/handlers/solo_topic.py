async def recibir_solo_en_topic(update, context):
    if update.message:
        print(f"✅ Chat ID: {update.effective_chat.id}")
        print(f"✅ Thread ID: {update.message.message_thread_id}")
        print(f"📝 Texto: {update.message.text}")
        
        await update.message.reply_text("Mensaje recibido. ID registrado en logs.")
    else:
        print("📛 Mensaje ignorado (sin mensaje)")
        return
