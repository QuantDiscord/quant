from __future__ import annotations as _

from typing import TypeVar, TYPE_CHECKING
from abc import ABC, abstractmethod

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.utils.cache.cache_manager import CacheManager


class Event:
    async def call(self) -> None:
        ...

    def emit(self, *args, **kwargs) -> Self:
        ...


class InternalEvent(ABC, Event):
    T = TypeVar("T")

    @staticmethod
    @abstractmethod
    def build(event: T, *args, **kwargs) -> T:
        ...


@attrs.define
class DiscordEvent(Event):
    event_api_name: EventTypes = attrs.field()
    cache_manager: CacheManager = attrs.field()

