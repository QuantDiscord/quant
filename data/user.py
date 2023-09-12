import datetime
from typing import Dict, List, Any

import attrs

from dispy.data.model import BaseModel
from dispy.utils.attrs_extensions import auto_converter


@attrs.define(field_transformer=auto_converter)
class User(BaseModel):
    username: str = attrs.field()
    member: Dict = attrs.field(default=None)
    user_id: int = attrs.field(alias="id", default=None)
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
    avatar_decoration_data: Any = attrs.field(default=None)

    @classmethod
    def from_dict_iter(cls, data):
        if data is not None:
            return [cls(**user_data) for user_data in data]

    @classmethod
    def from_dict(cls, data):
        if data is not None:
            return cls(**data)


@attrs.define(kw_only=True, field_transformer=auto_converter)
class GuildMember(User):
    username: str = attrs.field(default=None)
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    flags: int = attrs.field(default=0)
    pending: bool = attrs.field(default=False)
    permissions: str | None = attrs.field(default=None)
    nick: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    roles: List[Any] | None = attrs.field(default=None)
    join_time: datetime.datetime = attrs.field(alias="joined_at", default=0)
    premium_since: int | None = attrs.field(default=0)
    communication_disabled_until: int | None = attrs.field(default=0)
    user: User = attrs.field(default=None, converter=User.from_dict)

    @classmethod
    def from_dict(cls, data):
        if data is not None:
            return cls(**data)

    @classmethod
    def from_dict_iter(cls, data):
        if data is not None:
            return [cls(**member) for member in data]

