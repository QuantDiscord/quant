from __future__ import annotations

import datetime
from typing import List, Any

import attrs

from dispy.utils.attrs_extensions import execute_converters
from dispy.data.user import User


@attrs.define(kw_only=True, field_transformer=execute_converters)
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
    def from_dict_iter(cls, data) -> List[GuildMember] | None:
        if data is not None:
            return [cls(**member) for member in data]
