import enum
from typing import Any

import attrs

from .user import User
from .snowflake import Snowflake
from quant.utils.attrs_extensions import execute_converters


@attrs.define(field_transformer=execute_converters)
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
