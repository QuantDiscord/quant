import time
import asyncio
from typing import Dict, Any, Callable, TYPE_CHECKING, cast, TypeVar

if TYPE_CHECKING:
    from quant.impl.core.gateway import Gateway

from quant.utils.cache.cache_manager import CacheHandlers
from quant.impl.events.event import Event, InternalEvent
from quant.impl.events.types import EventTypes

EventT = TypeVar("EventT")


class EventFactory:
    def __init__(self, gateway: "Gateway") -> None:
        self.added_listeners: Dict[Event | InternalEvent, Callable] = {}
        self._listener_transformer: Dict[str, Event] = {}
        self.cache = gateway.cache

    def build_event(self, received_type: EventTypes, **details) -> Event | InternalEvent | None:
        if received_type not in self._listener_transformer:
            return

        event = self._listener_transformer[received_type]
        if event in self.added_listeners.keys():
            event_class = cast(event, self._listener_transformer[received_type])()
            return event_class.process_event(self.cache, **details)

    @staticmethod
    def build_from_class(event: EventT, *args: Any) -> EventT | None:
        try:
            return event().build(*args)
        except AttributeError:
            return

    async def dispatch(self, event: Event | InternalEvent) -> None:
        event_callback = self.added_listeners.get(type(event))

        if event_callback is None:
            return

        await event_callback(event)

    def add_event(self, event: Event | InternalEvent, callback: Callable) -> None:
        self.added_listeners[event] = callback

        if not hasattr(event, "API_EVENT_NAME"):
            return

        self._listener_transformer[event.API_EVENT_NAME] = event

    async def wait(self, event_type: EventTypes, condition: Callable, timeout: int = 5) -> None:
        ...

    @staticmethod
    def cache_item(event_name: EventTypes, **kwargs) -> None:
        cache_handler = CacheHandlers()
        handlers = {
            EventTypes.READY_EVENT: cache_handler.handle_ready,
            EventTypes.MESSAGE_CREATE: cache_handler.handle_message,
            EventTypes.VOICE_STATE_UPDATE: cache_handler.handle_voice_state_update,
            EventTypes.GUILD_CREATE: cache_handler.handle_guild,
            EventTypes.GUILD_DELETE: cache_handler.handle_guild_delete,
            EventTypes.CHANNEL_CREATE: cache_handler.handle_channel_create
        }

        if handler := handlers.get(event_name):
            handler(**kwargs)  # type: ignore
