from dispy.data.guild.messages.interactions.interaction import Interaction
from dispy.impl.events.event import BaseEvent
from dispy.impl.events.types import EventTypes


class InteractionCreateEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.INTERACTION_CREATE

    interaction: Interaction

    def process_event(self, _, **kwargs):
        self.interaction = Interaction(**kwargs)
