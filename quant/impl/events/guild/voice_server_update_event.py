from __future__ import annotations as _

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.entities.voice_server_update import VoiceServer
from quant.impl.events.event import DiscordEvent


@attrs.define(kw_only=True)
class VoiceServerUpdateEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.VOICE_SERVER_UPDATE)
    state: VoiceServer = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        return self
