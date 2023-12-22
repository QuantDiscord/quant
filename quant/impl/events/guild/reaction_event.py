from quant.entities.emoji import Reaction
from quant.impl.events import EventTypes
from quant.impl.events.event import Event
from quant.utils.cache.cache_manager import CacheManager


class ReactionAddEvent(Event):
    API_EVENT_NAME = EventTypes.MESSAGE_REACTION_ADD

    reaction: Reaction

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.reaction = Reaction(**kwargs)

        cache_manager.add_emoji(self.reaction)
        return self


class ReactionRemoveEvent(Event):
    API_EVENT_NAME = EventTypes.MESSAGE_REACTION_REMOVE

    reaction: Reaction

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.reaction = Reaction(**kwargs)

        cache_manager.add_emoji(self.reaction)
        return self
