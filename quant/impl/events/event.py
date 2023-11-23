from abc import ABCMeta, abstractmethod

from quant.utils.cache_manager import CacheManager
from quant.impl.events.types import EventTypes


class Event:
    __metaclass__ = ABCMeta

    API_EVENT_NAME: EventTypes

    @abstractmethod
    def process_event(self, cache_manager: CacheManager, **kwargs): ...
