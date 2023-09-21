from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message
from dispy.data.user import User
from dispy.impl.events.types import EventTypes
from dispy.utils.cache_manager import CacheManager


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
