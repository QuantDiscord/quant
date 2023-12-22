from quant.impl.events.types import EventTypes
from quant.entities.voice_state_update import VoiceState
from quant.impl.events.event import Event
from quant.utils.cache.cache_manager import CacheManager


class VoiceStateUpdateEvent(Event):
    API_EVENT_NAME = EventTypes.VOICE_STATE_UPDATE

    state: VoiceState

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.state = VoiceState(**kwargs)
        return self
