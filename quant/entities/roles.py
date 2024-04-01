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
from typing import List, Any

import attrs

from .snowflake import Snowflake
from .permissions import Permissions


@attrs.define(kw_only=True, hash=True)
class GuildRole:
    id: Snowflake = attrs.field()
    name: str = attrs.field()
    color: int = attrs.field()
    hoist: bool = attrs.field()
    icon: str | None = attrs.field()
    unicode_emoji: str | None = attrs.field()
    position: int = attrs.field()
    permissions: Permissions = attrs.field()
    managed: bool = attrs.field()
    mentionable: bool = attrs.field()
    tags: List[Any] = attrs.field()
    flags: int = attrs.field()

    @property
    def mention(self) -> str:
        return f"<@&{self.id}>"


def empty_role() -> GuildRole:
    return GuildRole(
        id=Snowflake(0),
        name="",
        color=0,
        hoist=False,
        icon=None,
        unicode_emoji=None,
        position=0,
        permissions=Permissions.NONE,
        managed=False,
        mentionable=False,
        tags=[],
        flags=0
    )
