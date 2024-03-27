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
from typing import Any

import attrs

from .user import User
from .snowflake import Snowflake


@attrs.define(hash=True)
class Webhook:
    webhook_url: str = attrs.field(alias="url")
    webhook_token: str = attrs.field(alias="token")
    webhook_avatar: str = attrs.field(alias="avatar")
    webhook_name: str = attrs.field(alias="name")
    webhook_id: Snowflake = attrs.field(alias="id")
    webhook_type: int = attrs.field(alias="type")
    guild_id: Snowflake | None = attrs.field(default=None)
    channel_id: Snowflake | None = attrs.field(default=None)
    user: User | None = attrs.field(default=None)
    application_id: Snowflake | None = attrs.field(default=None)
    source_guild: Any | None = attrs.field(default=None)
    source_channel: Any | None = attrs.field(default=None)


class WebhookTypes(enum.Enum):
    INCOMING = 1
    CHANNEL_FOLLOWER = 2
    APPLICATION = 3
