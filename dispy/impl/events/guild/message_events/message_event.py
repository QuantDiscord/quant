from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message
from dispy.impl.events.types import EventTypes
from dispy.utils.cache_manager import CacheManager


class MessageCreateEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.MESSAGE_CREATE

    message: Message

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.message = Message(**kwargs)

        cache_manager.add_message(self.message)
