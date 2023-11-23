import attrs

from .snowflake import Snowflake
from quant.utils.attrs_extensions import int_converter


@attrs.define(kw_only=True)
class VoiceServer:
    token: str = attrs.field(default=None)
    guild_id: Snowflake = attrs.field(default=0, converter=int_converter)
    endpoint: str | None = attrs.field(default=None)
