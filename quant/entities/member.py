import datetime
from typing import Any, List
from typing_extensions import Self

import attrs

from .user import User
from .model import BaseModel
from quant.utils.attrs_extensions import execute_converters


@attrs.define(kw_only=True, field_transformer=execute_converters)
class GuildMember(BaseModel):
    username: str = attrs.field(default=None)
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    flags: int = attrs.field(default=0)
    pending: bool = attrs.field(default=False)
    permissions: str | None = attrs.field(default=None)
    nick: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    roles: List[Any] | None = attrs.field(default=None)
    joined_at: datetime.datetime = attrs.field(default=0)
    premium_since: int | None = attrs.field(default=0)
    communication_disabled_until: int | None = attrs.field(default=0)
    user: User = attrs.field(default=None, converter=User.as_dict)
    unusual_dm_activity_until: Any = attrs.field(default=None)

    @classmethod
    def as_dict(cls, data):
        if data is not None:
            return cls(**data)

    @classmethod
    def as_dict_iter(cls, data) -> List[Self] | None:
        if data is not None:
            return [cls(**member) for member in data]
