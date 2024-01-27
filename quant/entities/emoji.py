from __future__ import annotations

from typing import List, Any, TYPE_CHECKING

import attrs

from .model import BaseModel


if TYPE_CHECKING:
    from .user import User
    from .member import GuildMember
    from .snowflake import Snowflake


@attrs.define
class PartialReaction(BaseModel):
    emoji_name: str = attrs.field(alias="name")
    emoji_id: 'Snowflake' = attrs.field(default=0, alias="id")
    animated: bool = attrs.field(default=False)

    def __str__(self) -> str:
        if self.emoji_id > 0:
            return f"<:{self.emoji_name}:{self.emoji_id}>"
        else:
            return self.emoji_name


@attrs.define
class Emoji(BaseModel):
    id: Snowflake = attrs.field()
    name: str = attrs.field()
    roles: List[Any] = attrs.field()
    user: User = attrs.field()
    require_colons: bool = attrs.field()
    managed: bool = attrs.field()
    animated: bool = attrs.field()
    available: bool = attrs.field()
    version: int = attrs.field()

    def __str__(self) -> str:
        if self.id > 0:
            return f"<:{self.name}:{self.id}>"
        else:
            return self.name


@attrs.define
class Reaction(BaseModel):
    user_id: Snowflake = attrs.field()
    type: int = attrs.field()
    message_id: Snowflake = attrs.field()
    message_author_id: Snowflake = attrs.field()
    member: GuildMember = attrs.field()
    emoji: PartialReaction = attrs.field()
    channel_id: Snowflake = attrs.field()
    burst: bool = attrs.field()
    guild_id: Snowflake = attrs.field()
    burst_colors: List[Any] = attrs.field()

    def __str__(self) -> str:
        return str(self.emoji)
