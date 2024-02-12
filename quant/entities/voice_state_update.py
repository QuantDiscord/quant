from datetime import datetime

import attrs

from .snowflake import Snowflake
from .member import GuildMember


@attrs.define(kw_only=True)
class VoiceState:
    guild_id: Snowflake = attrs.field()
    channel_id: Snowflake = attrs.field()
    user_id: Snowflake = attrs.field()
    member: GuildMember = attrs.field()
    session_id: str = attrs.field()
    deaf: bool = attrs.field()
    mute: bool = attrs.field()
    self_deaf: bool = attrs.field()
    self_mute: bool = attrs.field()
    self_stream: bool = attrs.field()
    self_video: bool = attrs.field()
    suppress: bool = attrs.field()
    request_to_speak_timestamp: datetime = attrs.field()
