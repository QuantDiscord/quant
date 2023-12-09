from ..event import Event
from quant.impl.events.types import EventTypes


class ReadyEvent(Event):
    API_EVENT_NAME: EventTypes = EventTypes.READY_EVENT

    def process_event(self, _, **kwargs):
        return self
