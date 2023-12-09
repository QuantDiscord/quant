from quant.entities.interactions.interaction import Interaction
from quant.impl.events.event import Event
from quant.impl.events.types import EventTypes


class InteractionCreateEvent(Event):
    API_EVENT_NAME: EventTypes = EventTypes.INTERACTION_CREATE

    interaction: Interaction

    def process_event(self, _, **kwargs):
        self.interaction = Interaction(**kwargs)
        return self
