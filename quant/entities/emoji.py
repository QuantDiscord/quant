"""
MIT License

Copyright (c) 2023 MagM1go

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
from __future__ import annotations

from typing import List, Any, TYPE_CHECKING

import attrs

from .model import BaseModel


if TYPE_CHECKING:
    from .user import User
    from .member import GuildMember
    from .snowflake import Snowflake


@attrs.define(hash=True)
class PartialReaction(BaseModel):
    emoji_name: str = attrs.field(alias="name")
    emoji_id: Snowflake = attrs.field(default=0, alias="id", hash=True)
    animated: bool = attrs.field(default=False)

    def __str__(self) -> str:
        if self.emoji_id > 0:
            return f"<:{self.emoji_name}:{self.emoji_id}>"
        else:
            return self.emoji_name


@attrs.define
class Emoji(BaseModel):
    id: Snowflake = attrs.field()
    name: str = attrs.field()
    roles: List[Any] = attrs.field()
    user: User = attrs.field()
    require_colons: bool = attrs.field()
    managed: bool = attrs.field()
    animated: bool = attrs.field()
    available: bool = attrs.field()
    version: int = attrs.field()

    def __str__(self) -> str:
        if self.id > 0:
            return f"<:{self.name}:{self.id}>"
        else:
            return self.name

    def __hash__(self) -> int:
        return hash(self.id)


@attrs.define
class Reaction(BaseModel):
    user_id: Snowflake = attrs.field()
    type: int = attrs.field()
    message_id: Snowflake = attrs.field()
    message_author_id: Snowflake = attrs.field()
    member: GuildMember = attrs.field()
    emoji: PartialReaction = attrs.field()
    channel_id: Snowflake = attrs.field()
    burst: bool = attrs.field()
    guild_id: Snowflake = attrs.field()
    burst_colors: List[Any] = attrs.field()

    def __str__(self) -> str:
        return str(self.emoji)

    def __hash__(self) -> int:
        return hash(self.emoji.emoji_id)
