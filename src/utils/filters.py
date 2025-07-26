from telegram import Message, Update
from telegram.ext import MessageFilter
from src.config import GROUP_ID, TOPIC_ID

class MentionedBotFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        if not message.entities:
            return False
        return any(
            entity.type == "mention" and
            message.text[entity.offset:entity.offset + entity.length].lower() == f"@{message.bot.username.lower()}"
            for entity in message.entities
        )

    def __call__(self, update: Update) -> bool:
        return update.message is not None and self.filter(update.message)


class TopicFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.chat.id == GROUP_ID and message.message_thread_id == TOPIC_ID

    def __call__(self, update: Update) -> bool:
        return update.message is not None and self.filter(update.message)
