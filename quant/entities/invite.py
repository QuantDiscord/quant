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
import enum
import datetime
from typing import Any

import attrs

from .guild import Guild
from .channel import Channel
from .user import User
from .snowflake import Snowflake


class InviteTargetType(enum.Enum):
    NONE = 0
    STREAM = 1
    EMBEDDED_APPLICATION = 2


@attrs.define(kw_only=True)
class _InviteMetadata:
    uses: int = attrs.field(default=0)
    max_uses: int = attrs.field(default=0)
    max_age: int = attrs.field(default=0)
    temporary: bool = attrs.field(default=False)
    created_at: datetime.datetime = attrs.field(default=None)


@attrs.define(kw_only=True)
class Invite:
    code: str
    guild_id: Snowflake | None = attrs.field(default=None)
    guild: Guild | None = attrs.field(default=None)
    channel: Channel | None = attrs.field(default=None)
    inviter: User | None = attrs.field(default=None)
    target_type: InviteTargetType | None = attrs.field(default=0)
    target_user: User | None = attrs.field(default=None)
    target_application: Any | None = attrs.field(default=None)
    approximate_presence_count: int | None = attrs.field(default=0)
    approximate_member_count: int | None = attrs.field(default=0)
    expires_at: datetime.datetime | None = attrs.field(default=None)
    stage_instance: Any | None = attrs.field(default=None)
    guild_scheduled_event: Any | None = attrs.field(default=None)
    metadata: _InviteMetadata | None = attrs.field(default=None)
    _type: int = attrs.field(alias="type", default=-1)
    _flags: int = attrs.field(alias="flags", default=-1)
