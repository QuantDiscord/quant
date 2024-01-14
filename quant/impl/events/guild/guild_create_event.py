import attrs
from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.impl.events.event import DiscordEvent
from quant.entities.guild import Guild


@attrs.define(kw_only=True)
class GuildCreateEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.GUILD_CREATE)
    guild: Guild = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        self.guild = Guild(**kwargs)
        self.cache_manager.add_guild(self.guild)

        return self
