from quant.data.guild.messages import Reaction
from quant.impl.events import EventTypes
from quant.impl.events.event import BaseEvent
from quant.utils.cache_manager import CacheManager


class ReactionAddEvent(BaseEvent):
    API_EVENT_NAME = EventTypes.MESSAGE_REACTION_ADD
    reaction: Reaction

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.reaction = Reaction(**kwargs)

        cache_manager.add_emoji(self.reaction)
