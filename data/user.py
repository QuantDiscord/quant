from typing import Any

import attrs

from dispy.data.guild.members import member
from dispy.data.model import BaseModel
from dispy.data.gateway.snowflake import Snowflake


@attrs.define(kw_only=True)
class User(BaseModel):
    user_id: int = attrs.field(alias="id", default=None, converter=Snowflake.object_id_from_snowflake)
    username: str = attrs.field()
    discriminator: str | None = attrs.field(default=None)
    display_name: str | None = attrs.field(default=None)
    global_name: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    is_bot: bool = attrs.field(alias="bot", default=False)
    is_system: bool = attrs.field(alias="system", default=False)
    mfa_enabled: bool = attrs.field(default=False)
    banner_hash: str = attrs.field(alias="banner", default=None)
    accent_color: int | None = attrs.field(default=None)
    banner_color: int | None = attrs.field(default=None)
    avatar_decoration: str | None = attrs.field(default=None)
    locale: str | None = attrs.field(default=None)
    flags: int = attrs.field(default=0)
    premium_type: int = attrs.field(default=0)
    public_flags: int = attrs.field(default=0)
    member: Any = attrs.field(default=None, converter=member.GuildMember.from_dict)

    @classmethod
    def from_dict(cls, data):
        if data is not None:
            return cls(**data)

    @classmethod
    def from_dict_iter(cls, data):
        if data is not None:
            return [cls(**user_data) for user_data in data]
