from dispy.impl.events.event import BaseEvent
from dispy.data.guild.guild_object import Guild
from dispy.impl.events.types import EventTypes
from dispy.utils.cache_manager import CacheManager


class GuildCreateEvent(BaseEvent):
    API_EVENT_NAME: EventTypes = EventTypes.GUILD_CREATE

    guild: Guild

    def process_event(self, cache_manager: CacheManager, **kwargs):
        self.guild = Guild(**kwargs)

        cache_manager.add_guild(self.guild)
