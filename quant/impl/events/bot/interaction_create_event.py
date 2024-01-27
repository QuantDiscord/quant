import attrs
from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.entities.interactions.interaction import Interaction
from quant.impl.events.event import DiscordEvent


@attrs.define(kw_only=True)
class InteractionCreateEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.INTERACTION_CREATE)
    interaction: Interaction = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        self.interaction = Interaction(**kwargs)
        return self
