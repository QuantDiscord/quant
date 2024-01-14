import attrs

from ..event import DiscordEvent
from ..types import EventTypes


@attrs.define(kw_only=True)
class ReadyEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.READY_EVENT)

    def emit(self, *args, **kwargs):
        return self
