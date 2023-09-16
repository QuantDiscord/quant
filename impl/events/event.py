from abc import ABCMeta, abstractmethod

from dispy.utils.cache_manager import CacheManager
from dispy.impl.events.types import EventTypes


class BaseEvent:
    __metaclass__ = ABCMeta

    API_EVENT_NAME: EventTypes

    @abstractmethod
    def process_event(self, cache_manager: CacheManager, **kwargs):
        ...
