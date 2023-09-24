from __future__ import annotations

from typing import List, Any

import attrs

from dispy.utils.attrs_extensions import execute_converters
from dispy.data.guild.members.member import GuildMember
from dispy.data.gateway.snowflake import Snowflake


@attrs.define(field_transformer=execute_converters)
class Emoji:
    emoji: Any = attrs.field()
    emoji_id: Snowflake = attrs.field(alias="id")
    name: str = attrs.field()
    emoji_type: str = attrs.field(alias="type")
    message_author_id: Snowflake = attrs.field(default=0)
    channel_id: Snowflake = attrs.field(default=0)
    message_id: Snowflake = attrs.field(default=0)
    burst: bool = attrs.field(default=False)
    guild_id: Snowflake = attrs.field(default=0)
    user_id: Snowflake = attrs.field(default=0)
    member: GuildMember = attrs.field(default=None, converter=GuildMember.from_dict)
    roles: List[Any] = attrs.field(default=None)
    require_colons: bool = attrs.field(default=False)
    managed: bool = attrs.field(default=False)
    animated: bool = attrs.field(default=False)
    available: bool = attrs.field(default=False)

    @classmethod
    def from_dict(cls, data):
        if data is not None:
            return cls(**data)

    def __str__(self) -> str:
        return f'{self.name}:{self.emoji_id}'
