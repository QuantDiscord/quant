from quant.impl.events.types import EventTypes
from quant.entities.voice_server_update import VoiceServer
from quant.impl.events.event import Event
from quant.utils.cache_manager import CacheManager


class VoiceServerUpdateEvent(Event):
    API_EVENT_NAME = EventTypes.VOICE_SERVER_UPDATE

    state: VoiceServer

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.state = VoiceServer(**kwargs)
