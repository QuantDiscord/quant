from abc import ABCMeta, abstractmethod


class BaseEvent:
    __metaclass__ = ABCMeta

    API_EVENT_NAME: str

    @abstractmethod
    def build_event(self, **kwargs):
        ...
