import inspect
from typing import Dict, List, TypeVar

from quant.impl import events
from quant.entities.factory.event_factory import EventFactory
from quant.utils.cache.cache_manager import CacheManager
from quant.utils.json_builder import MutableJsonBuilder

EventNameT = TypeVar("EventNameT", bound=str)


class EventController:
    def __init__(self, cache_manager: CacheManager) -> None:
        self.factory = EventFactory(cache_manager=cache_manager)

        self.hidden_events: List[MutableJsonBuilder[EventNameT, MutableJsonBuilder]] = []
        self.available: List[str] = [
            member[0][5:].upper() for member in inspect.getmembers(self) if member[0].startswith("when_")
        ]

    async def dispatch(self, event_name: str, details: MutableJsonBuilder | Dict) -> None:
        if event_name in self.available:
            callback = getattr(self, f"when_{event_name.lower()}")
            await callback(details)

    async def when_guild_create(self, payload: MutableJsonBuilder | Dict) -> None:
        event = self.factory.deserialize_guild_create_event(payload)
        await self.factory.dispatch(event)
