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
import enum
from datetime import datetime

import attrs

from .snowflake import Snowflake
from .model import BaseModel
from .user import User


class IntegrationTypes(enum.Enum):
    GUILD_INSTALL = 0
    USER_INSTALL = 1


class IntegrationExpireBehaviours(enum.Enum):
    NONE = -1
    REMOVE_ROLE = 0
    KICK = 1


@attrs.define(hash=True)
class IntegrationAccountObject(BaseModel):
    account_id: str = attrs.field(alias="id", default=None)
    name: str = attrs.field(default=None)


@attrs.define(hash=True)
class IntegrationApplicationObject(BaseModel):
    application_id: Snowflake = attrs.field(default=None)
    name: str = attrs.field(default=None)
    icon: str | None = attrs.field(default=None)
    description: str = attrs.field(default=None)
    bot: User | None = attrs.field(default=None)


@attrs.define(kw_only=True, hash=True)
class Integration:
    integration_id: Snowflake = attrs.field(alias="id", default=0)
    integration_name: str = attrs.field(default=None, alias="name")
    integration_type: str = attrs.field(default=None, alias="type")
    enabled: bool = attrs.field(default=False)
    syncing: bool = attrs.field(default=False)
    role_id: Snowflake = attrs.field(default=0)
    enable_emoticons: bool = attrs.field(default=False)
    expire_behaviour: IntegrationExpireBehaviours = attrs.field(
        default=IntegrationExpireBehaviours.NONE, converter=IntegrationExpireBehaviours
    )
    expire_grace_period: int = attrs.field(default=0)
    user: User = attrs.field(default=None)
    account: IntegrationAccountObject = attrs.field(default=None)
    synced_at: datetime = attrs.field(default=None)
    subscriber_count: int = attrs.field(default=0)
    revoked: bool = attrs.field(default=False)
    application: IntegrationApplicationObject = attrs.field(default=None)
