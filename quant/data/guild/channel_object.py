from typing import Any, List
from datetime import datetime

import attrs

from quant.data.user import User
from quant.data.guild.messages.emoji import Reaction
from quant.data.gateway.snowflake import Snowflake
from quant.utils.attrs_extensions import iso_to_datetime, int_converter
from quant.data.model import BaseModel


@attrs.define(kw_only=True)
class Channel(BaseModel):
    channel_id = attrs.field(alias="id", default=0, converter=int_converter)
    channel_type = attrs.field(alias="type", default=0, converter=int_converter)
    guild_id: Snowflake = attrs.field(default=0, converter=int_converter)
    position: int = attrs.field(default=0, converter=int_converter)
    permission_overwrites: Any = attrs.field(default=None)
    name: str = attrs.field(default=None)
    topic: str = attrs.field(default=None)
    nsfw: bool = attrs.field(default=False)
    version: str = attrs.field(default=None, repr=False)
    status: str = attrs.field(default=None, repr=False)
    theme_color: str = attrs.field(default=None, repr=False)
    icon_emoji: str = attrs.field(default=None, repr=False)
    template: str = attrs.field(default=None, repr=False)
    last_message_id: Snowflake = attrs.field(default=0, converter=int_converter)
    bitrate: int = attrs.field(default=0, converter=int_converter)
    user_limit: int = attrs.field(default=0, converter=int_converter)
    rate_limit_per_user: int = attrs.field(default=0, converter=int_converter)
    recipients: List[User] = attrs.field(default=None, converter=User.as_dict_iter)
    icon: str = attrs.field(default=None)
    owner_id: Snowflake = attrs.field(default=0, converter=int_converter)
    application_id: Snowflake = attrs.field(default=0, converter=int_converter)
    managed: bool = attrs.field(default=False)
    parent_id: Snowflake = attrs.field(default=0, converter=int_converter)
    last_pin_timestamp: datetime = attrs.field(default=None, converter=iso_to_datetime)
    rtc_region: str = attrs.field(default=None)
    video_quality_mode: int = attrs.field(default=0, converter=int_converter)
    message_count: int = attrs.field(default=0, converter=int_converter)
    member_count: int = attrs.field(default=0, converter=int_converter)
    thread_metadata: Any = attrs.field(default=None)
    thread_member: Any = attrs.field(alias="member", default=None)
    default_auto_archive_duration: int = attrs.field(default=0, converter=int_converter)
    permissions: str = attrs.field(default=None)
    flags: int = attrs.field(default=0, converter=int_converter)
    total_message_sent: int = attrs.field(default=0, converter=int_converter)
    available_tags: List[Any] = attrs.field(default=None)
    applied_tags: List[Snowflake] = attrs.field(default=None)
    default_reaction_emoji: List[Reaction] = attrs.field(default=None)
    default_thread_rate_limit_per_user: int = attrs.field(default=0, converter=int_converter)
    default_sort_order: int = attrs.field(default=0, converter=int_converter)
    default_forum_layout: int = attrs.field(default=0, converter=int_converter)

    @classmethod
    def as_dict_iter(cls, data):
        if data is not None:
            return [cls(**i) for i in data]
