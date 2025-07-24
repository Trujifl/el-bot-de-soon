from telegram import Message
from telegram.ext import MessageFilter
from src.config import TOPIC_ID


class MentionedBotFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return (
            message is not None
            and message.entities is not None
            and any(
                entity.type == "mention"
                and message.parse_entity(entity).lower().startswith("@")
                for entity in message.entities
            )
        )


class TopicFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return (
            message is not None
            and message.is_topic_message
            and message.message_thread_id == TOPIC_ID
        )
