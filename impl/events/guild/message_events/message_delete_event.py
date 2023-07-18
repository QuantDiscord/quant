from dispy.impl.events.event import BaseEvent
from dispy.data.guild.messages.message import Message
from dispy.data.user import User


class MessageDeleteEvent(BaseEvent):
    API_EVENT_NAME: str = "MESSAGE_DELETE"

    author: User
    message: Message

    def process_event(self, cache_manager, **kwargs):
        message = cache_manager.get_message(int(kwargs.get("id")))
        if message is not None:
            self.message = message

    @classmethod
    def set_author(cls, user: User):
        cls.author = user
