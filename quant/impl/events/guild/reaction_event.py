import attrs
from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.entities.emoji import Reaction
from quant.impl.events.event import DiscordEvent


@attrs.define(kw_only=True)
class ReactionAddEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.MESSAGE_REACTION_ADD)
    reaction: Reaction = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        return self


@attrs.define(kw_only=True)
class ReactionRemoveEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.MESSAGE_REACTION_REMOVE)
    reaction: Reaction = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        return self
