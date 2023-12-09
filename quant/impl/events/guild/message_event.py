from quant.entities.user import User
from quant.impl.events.event import Event
from quant.entities.message import Message
from quant.impl.events.types import EventTypes
from quant.utils.cache_manager import CacheManager


class MessageCreateEvent(Event):
    API_EVENT_NAME: EventTypes = EventTypes.MESSAGE_CREATE

    message: Message

    def process_event(self, cache_manager: CacheManager, **kwargs):
        if kwargs is None:
            return

        self.message = Message(**kwargs)

        cache_manager.add_message(self.message)


class MessageEditEvent(Event):
    API_EVENT_NAME: EventTypes = EventTypes.MESSAGE_UPDATE

    old_message: Message
    new_message: Message

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.new_message = Message(**kwargs)
        message = cache_manager.get_message(int(kwargs.get("id")))
        if message is None:
            return

        self.old_message = message

        return self


class MessageDeleteEvent(Event):
    API_EVENT_NAME: EventTypes = EventTypes.MESSAGE_DELETE

    author: User
    message: Message

    def process_event(self, cache_manager: CacheManager, **kwargs):
        message = cache_manager.get_message(int(kwargs.get("id")))
        if message is not None:
            self.message = message

        return self

    @classmethod
    def set_author(cls, user: User):
        cls.author = user
