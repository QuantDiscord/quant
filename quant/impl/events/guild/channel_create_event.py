from __future__ import annotations as _

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.impl.events.event import DiscordEvent
from quant.entities.channel import Channel


@attrs.define(kw_only=True)
class ChannelCreateEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.CHANNEL_CREATE)
    channel: Channel = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        self.channel = Channel(**kwargs)
        self.cache_manager.add_channel(self.channel)

        return self
