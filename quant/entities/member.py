from __future__ import annotations

import datetime
from typing import Any, List, TYPE_CHECKING
from typing_extensions import Self

import attrs

if TYPE_CHECKING:
    from .user import User

from .snowflake import Snowflake
from .model import BaseModel
from .roles import GuildRole
from .permissions import Permissions


@attrs.define(kw_only=True)
class GuildMember(BaseModel):
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    flags: int = attrs.field(default=0)
    pending: bool = attrs.field(default=False)
    permissions: Permissions | None = attrs.field(default=None)
    nick: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    roles: List[GuildRole] | None = attrs.field(default=None)
    joined_at: datetime.datetime = attrs.field(default=0)
    premium_since: int | None = attrs.field(default=0)
    communication_disabled_until: int | None = attrs.field(default=0)
    user: User = attrs.field(default=None)
    unusual_dm_activity_until: Any = attrs.field(default=None)

    @property
    def id(self) -> Snowflake:
        return self.user.id

    def get_avatar(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png?size=1024"
