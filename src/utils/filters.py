from telegram import Update
from telegram.ext import BaseFilter

class MentionedBotFilter(BaseFilter):
    def filter(self, message: Update.message) -> bool:
        if not message.entities or not message.text or not message.bot:
            return False
        return any(
            e.type == "mention" and f"@{message.bot.username}" in message.text
            for e in message.entities
        )

class TopicFilter(BaseFilter):
    def filter(self, message: Update.message) -> bool:
        return message.message_thread_id == 8183 
