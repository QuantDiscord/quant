from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message


class MessageEditEvent(BaseEvent):
    API_EVENT_NAME: str = "MESSAGE_UPDATE"

    previous_message: Message
    current_message: Message

    def build_event(self, **kwargs):
        self.current_message = Message(**kwargs)
