from abc import ABCMeta, abstractmethod


class BaseEvent:
    __metaclass__ = ABCMeta

    API_EVENT_NAME: str

    @abstractmethod
    def process_event(self, cache_manager, **kwargs):
        ...
