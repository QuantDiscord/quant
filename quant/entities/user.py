from typing import Any
from typing_extensions import Self

import attrs

from quant.entities.model import BaseModel

from .snowflake import Snowflake


@attrs.define
class User(BaseModel):
    username: str = attrs.field()
    id: Snowflake = attrs.field(default=0)
    discriminator: str | None = attrs.field(default=None)
    display_name: str | None = attrs.field(default=None)
    global_name: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    bot: bool = attrs.field(default=False)
    system: bool = attrs.field(default=False)
    mfa_enabled: bool = attrs.field(default=False)
    banner: str = attrs.field(default=None)
    accent_color: int | None = attrs.field(default=None)
    banner_color: int | None = attrs.field(default=None)
    avatar_decoration: str | None = attrs.field(default=None)
    locale: str | None = attrs.field(default=None)
    flags: int = attrs.field(default=0)
    premium_type: int = attrs.field(default=0)
    public_flags: int = attrs.field(default=0)
    avatar_decoration_data: Any = attrs.field(default=None)
    verified: bool = attrs.field(default=False)
    _email: str = attrs.field(default=None, alias="email", repr=False)
    member: Any = attrs.field(default=None)

    def get_avatar(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png?size=1024"
