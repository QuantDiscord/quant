from dispy.impl.events.event import BaseEvent
from dispy.data.guild.guild_object import Guild


class GuildCreateEvent(BaseEvent):
    API_EVENT_NAME: str = "GUILD_CREATE"

    guild: Guild

    def process_event(self, cache_manager, **kwargs):
        self.guild = Guild(**kwargs)

        cache_manager.add_cache_guild(self.guild.guild_id)
