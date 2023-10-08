from quant.impl.events.event import BaseEvent
from quant.data.guild.messages.message import Message
from quant.data.user import User
from quant.impl.events.types import EventTypes
from quant.utils.cache_manager import CacheManager


class MessageDeleteEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.MESSAGE_DELETE

    author: User
    message: Message

    def process_event(self, cache_manager: CacheManager, **kwargs):
        message = cache_manager.get_message(int(kwargs.get("id")))
        if message is not None:
            self.message = message

    @classmethod
    def set_author(cls, user: User):
        cls.author = user
