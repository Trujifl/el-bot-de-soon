from telegram import Message
from telegram.ext import filters
from src.config import GROUP_ID, TOPIC_ID


class MentionedBotFilter(filters.BaseFilter):
    def filter(self, message: Message) -> bool:
        if not message.entities:
            return False
        return any(
            entity.type == "mention" and
            message.text[entity.offset:entity.offset + entity.length].lower() == f"@{message.bot.username.lower()}"
            for entity in message.entities
        )


class TopicFilter(filters.BaseFilter):
    def filter(self, message: Message) -> bool:
        return message.chat.id == GROUP_ID and message.message_thread_id == TOPIC_ID
