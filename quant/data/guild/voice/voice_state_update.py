from __future__ import annotations

from datetime import datetime

import attrs

from quant.data.gateway.snowflake import Snowflake
from quant.utils.attrs_extensions import iso_to_datetime, int_converter
from quant.data.guild.members.member import GuildMember


@attrs.define(kw_only=True)
class VoiceState:
    guild_id: Snowflake = attrs.field(default=0, converter=int_converter)
    channel_id: Snowflake = attrs.field(default=0, converter=int_converter)
    user_id: Snowflake = attrs.field(default=0, converter=int_converter)
    member: GuildMember = attrs.field(default=None, converter=GuildMember.as_dict)
    session_id: str = attrs.field(default=None)
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    self_deaf: bool = attrs.field(default=False)
    self_mute: bool = attrs.field(default=False)
    self_stream: bool = attrs.field(default=False)
    self_video: bool = attrs.field(default=False)
    suppress: bool = attrs.field(default=False)
    request_to_speak_timestamp: datetime = attrs.field(default=None, converter=iso_to_datetime)

    @classmethod
    def as_dict(cls, data) -> VoiceState | None:
        if data is not None:
            return cls(**data)

    @classmethod
    def as_dict_iter(cls, data):
        if data is not None:
            return [cls(**voice_data) for voice_data in data]
