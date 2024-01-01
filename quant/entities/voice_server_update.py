import attrs

from .snowflake import Snowflake


@attrs.define(kw_only=True)
class VoiceServer:
    token: str = attrs.field(default=None)
    guild_id: Snowflake = attrs.field(default=0)
    endpoint: str | None = attrs.field(default=None)
