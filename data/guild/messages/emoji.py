from __future__ import annotations

from typing import List, Any

import attrs

from dispy.data.user import User
from dispy.utils.attrs_extensions import execute_converters


@attrs.define(field_transformer=execute_converters)
class Emoji:
    emoji_id: int = attrs.field(alias="id")
    name: str = attrs.field()
    user: User = attrs.field(default=None, converter=User.from_dict)
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
