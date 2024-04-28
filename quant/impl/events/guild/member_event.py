from __future__ import annotations as _

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.entities.user import User
from quant.entities.member import GuildMember
from quant.entities.snowflake import Snowflake
from quant.impl.events.types import EventTypes
from quant.impl.events.event import DiscordEvent


@attrs.define(kw_only=True)
class MemberJoinEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.GUILD_MEMBER_ADD)
    guild_id: Snowflake = attrs.field(default=Snowflake())
    member: GuildMember = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        guild_id = kwargs.get("guild_id")
        self.guild_id = guild_id
        self.member = self.entity_factory.deserialize_member(kwargs, guild_id=guild_id)
        return self


@attrs.define(kw_only=True)
class MemberLeaveEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.GUILD_MEMBER_REMOVE)
    guild_id: Snowflake = attrs.field(default=Snowflake())
    user: User = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        self.guild_id = kwargs.get("guild_id")
        self.user = self.entity_factory.deserialize_user(kwargs)
        return self
