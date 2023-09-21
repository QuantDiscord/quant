from typing import Any

import attrs

from dispy.data.user import User


@attrs.define
class Webhook:
    webhook_url: str = attrs.field(alias="url")
    webhook_token: str = attrs.field(alias="token")
    webhook_avatar: str = attrs.field(alias="avatar")
    webhook_name: str = attrs.field(alias="name")
    webhook_id: int = attrs.field(alias="id")
    webhook_type: int = attrs.field(alias="type")
    guild_id: int | None = attrs.field(default=None)
    channel_id: int | None = attrs.field(default=None)
    user: User | None = attrs.field(default=None)
    application_id: int | None = attrs.field(default=None)
    source_guild: Any | None = attrs.field(default=None)
    source_channel: Any | None = attrs.field(default=None)
