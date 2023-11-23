from quant.impl.events.event import Event
from quant.entities.guild import Guild
from quant.impl.events.types import EventTypes
from quant.utils.cache_manager import CacheManager


class GuildCreateEvent(Event):
    API_EVENT_NAME: EventTypes = EventTypes.GUILD_CREATE

    guild: Guild

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.guild = Guild(**kwargs)

        print(self.guild.channels)
        cache_manager.add_guild(self.guild)
