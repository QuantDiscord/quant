import inspect
from typing import Dict, List, TypeVar, Callable, Set, overload

from quant.impl.events.types import EventTypes
from quant.entities.factory.event_factory import EventFactory, EventT
from quant.utils.cache.cache_manager import CacheManager
from quant.utils.json_builder import MutableJsonBuilder

EventNameT = TypeVar("EventNameT", bound=str)


class EventController:
    def __init__(self, factory: EventFactory) -> None:
        self.factory = factory
        self.available: List[str] = [
            member[0][5:].upper() for member in inspect.getmembers(self) if member[0].startswith("when_")
        ]
        self._waiting_events: Set[EventTypes, Callable] = set()

    async def wait(self, event_type: EventTypes, condition: Callable, timeout: int = 5) -> None:
        ...

    @overload
    async def dispatch(self, event: EventT) -> None:
        ...

    @overload
    async def dispatch(self, event_name: str, details: MutableJsonBuilder | Dict) -> None:
        ...

    async def dispatch(self, *args) -> None:
        if len(args) == 1:
            event = args[0]
            event_callback = self.factory.added_listeners.get(type(event))
            if event_callback is not None:
                await event_callback(event)

            if event is not None:
                await event.call()

        if len(args) == 2:
            event_name, details = args
            if event_name not in self.available:
                return

            callback = getattr(self, f"when_{event_name.lower()}")
            await callback(details)

    async def when_guild_create(self, payload: MutableJsonBuilder | Dict) -> None:
        event = self.factory.deserialize_guild_create_event(payload)
        await self.dispatch(event)

    async def when_interaction_create(self, payload: MutableJsonBuilder | Dict) -> None:
        event = self.factory.deserialize_interaction_event(payload)
        await self.dispatch(event)

    async def when_message_create(self, payload: MutableJsonBuilder | Dict) -> None:
        event = self.factory.deserialize_message_create_event(payload)
        await self.dispatch(event)
