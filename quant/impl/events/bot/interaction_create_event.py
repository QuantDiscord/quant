from quant.data.guild.messages.interactions.interaction import Interaction
from quant.impl.events.event import BaseEvent
from quant.impl.events.types import EventTypes


class InteractionCreateEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.INTERACTION_CREATE

    interaction: Interaction

    def process_event(self, _, **kwargs):
        self.interaction = Interaction(**kwargs)
