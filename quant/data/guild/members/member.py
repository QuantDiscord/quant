from __future__ import annotations

import datetime
from typing import List, Any

import attrs

from quant.utils.attrs_extensions import execute_converters, iso_to_datetime
from quant.data.user import User


@attrs.define(kw_only=True, field_transformer=execute_converters)
class GuildMember:
    username: str = attrs.field(default=None)
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    flags: int = attrs.field(default=0)
    pending: bool = attrs.field(default=False)
    permissions: str | None = attrs.field(default=None)
    nick: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    roles: List[Any] | None = attrs.field(default=None)
    joined_at: datetime.datetime = attrs.field(default=0, converter=iso_to_datetime)
    premium_since: int | None = attrs.field(default=0)
    communication_disabled_until: int | None = attrs.field(default=0)
    user: User = attrs.field(default=None, converter=User.as_dict)
    unusual_dm_activity_until: Any = attrs.field(default=None)

    @classmethod
    def as_dict(cls, data):
        if data is not None:
            return cls(**data)

    @classmethod
    def as_dict_iter(cls, data) -> List[GuildMember] | None:
        if data is not None:
            return [cls(**member) for member in data]
