"""
MIT License

Copyright (c) 2023 MagM1go

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
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
    deaf: bool = attrs.field()
    mute: bool = attrs.field()
    flags: int = attrs.field()
    pending: bool = attrs.field(repr=False)
    permissions: Permissions | None = attrs.field(repr=False)
    nick: str | None = attrs.field()
    avatar: str | None = attrs.field()
    roles: List[GuildRole] | None = attrs.field(repr=False)
    joined_at: datetime.datetime = attrs.field()
    premium_since: int | None = attrs.field()
    communication_disabled_until: int | None = attrs.field()
    user: User = attrs.field()
    guild_id: Snowflake | int = attrs.field()
    unusual_dm_activity_until: Any = attrs.field()

    def __hash__(self) -> int:
        return hash(self.user)

    @property
    def mention(self) -> str:
        return f"<@{self.user.id}>"

    @property
    def id(self) -> Snowflake:
        return self.user.id

    def get_avatar(self, size: int = 1024) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png?size={size}"

    async def add_role(self, role: GuildRole | Snowflake | int) -> None:
        if isinstance(role, GuildRole):
            role = role.id

        await self.client.rest.add_guild_member_role(
            guild_id=self.guild_id,
            role_id=role,
            user_id=self.id
        )

    def get_permissions(self) -> Permissions:
        permissions = Permissions.NONE

        guild = self.client.cache.get_guild(guild_id=self.guild_id)
        if self.id == guild.owner_id or self.permissions & Permissions.ADMINISTRATOR:
            return Permissions.ADMINISTRATOR

        roles = [guild.get_everyone_role()] + self.roles
        for role in roles:
            permissions |= role.permissions

        return permissions
