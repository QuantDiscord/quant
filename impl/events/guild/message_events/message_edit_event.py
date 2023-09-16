from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message
from dispy.impl.events.types import EventTypes
from dispy.utils.cache_manager import CacheManager


class MessageEditEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.MESSAGE_UPDATE

    old_message: Message
    new_message: Message

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.new_message = Message(**kwargs)
        message = cache_manager.get_message(int(kwargs.get("id")))
        if message is None:
            return

        self.old_message = message
