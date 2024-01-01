from datetime import datetime
from typing_extensions import Self

import attrs

from .snowflake import Snowflake
from .member import GuildMember


@attrs.define(kw_only=True)
class VoiceState:
    guild_id: Snowflake = attrs.field(default=0)
    channel_id: Snowflake = attrs.field(default=0)
    user_id: Snowflake = attrs.field(default=0)
    member: GuildMember = attrs.field(default=None, converter=GuildMember.as_dict)
    session_id: str = attrs.field(default=None)
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    self_deaf: bool = attrs.field(default=False)
    self_mute: bool = attrs.field(default=False)
    self_stream: bool = attrs.field(default=False)
    self_video: bool = attrs.field(default=False)
    suppress: bool = attrs.field(default=False)
    request_to_speak_timestamp: datetime = attrs.field(default=None)

    @classmethod
    def as_dict(cls, data) -> Self | None:
        if data is not None:
            return cls(**data)

    @classmethod
    def as_dict_iter(cls, data):
        if data is not None:
            return [cls(**voice_data) for voice_data in data]
