from typing import Dict, Any

import attrs

from dispy.data.model import BaseModel
from dispy.utils.attrs_extensions import execute_converters


@attrs.define(field_transformer=execute_converters)
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
    def from_dict(cls, data):
        if data is not None:
            return cls(**data)

    @classmethod
    def from_dict_iter(cls, data):
        if data is not None:
            return [cls(**user_data) for user_data in data]
