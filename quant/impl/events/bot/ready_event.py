from ..event import BaseEvent
from quant.impl.events.types import EventTypes


class ReadyEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.READY_EVENT

    def process_event(self, _, **kwargs):
        ...
