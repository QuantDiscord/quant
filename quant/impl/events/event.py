from abc import ABC, abstractmethod

from typing_extensions import Self

from quant.utils.cache.cache_manager import CacheManager
from .types import EventTypes


class Event(ABC):
    API_EVENT_NAME: EventTypes

    @abstractmethod
    def process_event(self, cache_manager: CacheManager, **kwargs) -> Self: ...


class InternalEvent(ABC):
    @abstractmethod
    def process_event(self, cache_manager: CacheManager, **kwargs) -> Self: ...
