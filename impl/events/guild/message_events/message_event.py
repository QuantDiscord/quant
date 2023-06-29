from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message


class MessageEvent(BaseEvent):
    API_EVENT_NAME: str = "MESSAGE_CREATE"

    message: Message

    def build_event(self, **kwargs):
        self.message = Message(**kwargs)
