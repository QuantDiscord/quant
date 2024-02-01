from __future__ import annotations

import datetime
from typing import Any, List, TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from .user import User

from .model import BaseModel
from .snowflake import Snowflake
from .roles import GuildRole
from .permissions import Permissions


@attrs.define(kw_only=True)
class GuildMember(BaseModel):
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    flags: int = attrs.field(default=0)
    pending: bool = attrs.field(default=False, repr=False)
    permissions: Permissions | None = attrs.field(default=None)
    nick: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    roles: List[GuildRole] | None = attrs.field(default=None, repr=False)
    joined_at: datetime.datetime = attrs.field(default=0)
    premium_since: int | None = attrs.field(default=0)
    communication_disabled_until: int | None = attrs.field(default=0)
    user: User = attrs.field(default=None)
    guild_id: Snowflake | int = attrs.field()
    unusual_dm_activity_until: Any = attrs.field(default=None)

    @property
    def mention(self) -> str:
        return f"<@{self.user.id}>"

    @property
    def id(self) -> Snowflake:
        return self.user.id

    def get_avatar(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png?size=1024"

    async def add_role(self, role: GuildRole | Snowflake | int) -> None:
        if isinstance(role, GuildRole):
            role = role.id

        await self.client.rest.add_guild_member_role(
            guild_id=self.guild_id,
            role_id=role,
            user_id=self.id
        )
