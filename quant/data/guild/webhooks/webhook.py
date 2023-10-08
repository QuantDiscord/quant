from typing import Any

import attrs

from quant.data.user import User
from quant.data.gateway.snowflake import Snowflake


@attrs.define
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
