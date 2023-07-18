from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message


class MessageEvent(BaseEvent):
    API_EVENT_NAME: str = "MESSAGE_CREATE"

    message: Message

    def process_event(self, cache_manager, **kwargs):
        self.message = Message(**kwargs)

        cache_manager.add_cache_message(self.message)
