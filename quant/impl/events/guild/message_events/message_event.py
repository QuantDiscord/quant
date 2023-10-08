from quant.impl.events.event import BaseEvent
from quant.data.guild.messages.message import Message
from quant.impl.events.types import EventTypes
from quant.utils.cache_manager import CacheManager


class MessageCreateEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.MESSAGE_CREATE

    message: Message

    def process_event(self, cache_manager: CacheManager, **kwargs):
        if kwargs is None:
            return

        self.message = Message(**kwargs)

        cache_manager.add_message(self.message)
