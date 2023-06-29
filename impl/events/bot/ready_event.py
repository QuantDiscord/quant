from ..event import BaseEvent


class ReadyEvent(BaseEvent):
    API_EVENT_NAME = "READY"

    @staticmethod
    def build_event(**kwargs):
        ...
