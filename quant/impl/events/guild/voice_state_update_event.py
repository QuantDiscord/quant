from __future__ import annotations as _

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.entities.voice_state_update import VoiceState
from quant.impl.events.event import DiscordEvent


@attrs.define(kw_only=True)
class VoiceStateUpdateEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.VOICE_STATE_UPDATE)
    state: VoiceState = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        self.state = VoiceState(**kwargs)
        return self
