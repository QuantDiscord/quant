from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message
from dispy.data.user import User


class MessageDeleteEvent(BaseEvent):
    API_EVENT_NAME: str = "MESSAGE_DELETE"

    author: User
    message: Message

    def build_event(self, **kwargs):
        self.message = Message(**kwargs)

    @classmethod
    def set_author(cls, user: User):
        cls.author = user
