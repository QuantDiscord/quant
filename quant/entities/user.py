"""
MIT License

Copyright (c) 2024 MagM1go

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations as _

from typing import Any

import attrs

from quant.entities.model import BaseModel

from .snowflake import Snowflake


@attrs.define(hash=True)
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

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    def get_avatar(self, size: int = 1024) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png?size={size}"

    async def fetch(self) -> User:
        return await self.client.rest.fetch_user(user_id=self.id)
