
from telegram import Message, Update
from telegram.ext.filters import BaseFilter
from src.config import GROUP_ID, TOPIC_ID

class MentionedBotFilter(BaseFilter):
    def filter(self, message: Message) -> bool:
        if not message.text:
            return False
        bot_username = message.bot.username.lower()
        return message.text.strip().lower().startswith(f"@{bot_username}")

    def __call__(self, update: Update) -> bool:
        return update.message is not None and self.filter(update.message)


class TopicFilter(BaseFilter):
    def filter(self, message: Message) -> bool:
        return message.chat.id == GROUP_ID and message.message_thread_id == TOPIC_ID

    def __call__(self, update: Update) -> bool:
        return update.message is not None and self.filter(update.message)
