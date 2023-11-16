from typing import List, Any, Dict

import attrs

from quant.utils.attrs_extensions import execute_converters, int_converter
from quant.data.user import User
from quant.data.guild.members.member import GuildMember
from quant.data.gateway.snowflake import Snowflake
from quant.data.model import BaseModel


@attrs.define(field_transformer=execute_converters)
class PartialReaction(BaseModel):
    emoji_name: str = attrs.field(alias="name")
    emoji_id: Snowflake = attrs.field(default=0, alias="id")
    animated: bool = attrs.field(default=False)

    def __str__(self) -> str:
        if self.emoji_id > 0:
            return f"<:{self.emoji_name}:{self.emoji_id}>"
        else:
            return self.emoji_name


@attrs.define(field_transformer=execute_converters)
class Reaction(BaseModel):
    user_id: Snowflake = attrs.field(default=0, converter=int_converter)
    reaction_type: int = attrs.field(default=0, alias="type", converter=int_converter)
    message_id: Snowflake = attrs.field(default=0, converter=int_converter)
    message_author_id: Snowflake = attrs.field(default=0, converter=int_converter)
    member: GuildMember = attrs.field(default=None, converter=GuildMember.as_dict)
    emoji: PartialReaction = attrs.field(default=None, converter=PartialReaction.as_dict)
    channel_id: Snowflake = attrs.field(default=0, converter=int_converter)
    burst: bool = attrs.field(default=False)
    guild_id: Snowflake = attrs.field(default=0, converter=int_converter)
    burst_colors: List[Any] = attrs.field(default=None)

    def __str__(self) -> str:
        return str(self.emoji)


@attrs.define(field_transformer=execute_converters)
class Emoji(BaseModel):
    emoji_id: Snowflake = attrs.field(alias="id")
    emoji_name: str = attrs.field(alias="name")
    roles: List[Any] = attrs.field(default=None)
    user: User = attrs.field(default=None, converter=User.as_dict)
    require_colons: bool = attrs.field(default=False)
    managed: bool = attrs.field(default=False)
    animated: bool = attrs.field(default=False)
    available: bool = attrs.field(default=False)
    _version: int = attrs.field(default=0, alias="version")

    @classmethod
    def as_dict(cls, data):
        if data is not None:
            return cls(**data)

    def __str__(self) -> str:
        if self.emoji_id > 0:
            return f"<:{self.emoji_name}:{self.emoji_id}>"
        else:
            return self.emoji_name
