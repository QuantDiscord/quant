from quant.impl.events.types import EventTypes
from quant.data.guild.voice.voice_state_update import VoiceState
from quant.impl.events.event import BaseEvent
from quant.utils.cache_manager import CacheManager


class VoiceStateUpdateEvent(BaseEvent):
    API_EVENT_NAME = EventTypes.VOICE_STATE_UPDATE

    state: VoiceState

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.state = VoiceState(**kwargs)
