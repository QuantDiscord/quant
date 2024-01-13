from datetime import datetime
from typing import Any, List

import attrs

from .emoji import Reaction
from .model import BaseModel
from .snowflake import Snowflake
from .user import User
from quant.utils.attrs_extensions import execute_converters


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Channel(BaseModel):
    channel_id = attrs.field(alias="id", default=0)
    channel_type = attrs.field(alias="type", default=0)
    guild_id: Snowflake = attrs.field(default=0)
    position: int = attrs.field(default=0)
    permission_overwrites: Any = attrs.field(default=None)
    name: str = attrs.field(default=None)
    topic: str = attrs.field(default=None)
    nsfw: bool = attrs.field(default=False)
    version: str = attrs.field(default=None, repr=False)
    status: str = attrs.field(default=None, repr=False)
    theme_color: str = attrs.field(default=None, repr=False)
    icon_emoji: str = attrs.field(default=None, repr=False)
    template: str = attrs.field(default=None, repr=False)
    last_message_id: Snowflake = attrs.field(default=0)
    bitrate: int = attrs.field(default=0)
    user_limit: int = attrs.field(default=0)
    rate_limit_per_user: int = attrs.field(default=0)
    recipients: List[User] = attrs.field(default=None, converter=User.as_dict_iter)
    icon: str = attrs.field(default=None)
    owner_id: Snowflake = attrs.field(default=0)
    application_id: Snowflake = attrs.field(default=0)
    managed: bool = attrs.field(default=False)
    parent_id: Snowflake = attrs.field(default=0)
    last_pin_timestamp: datetime = attrs.field(default=None)
    rtc_region: str = attrs.field(default=None)
    video_quality_mode: int = attrs.field(default=0)
    message_count: int = attrs.field(default=0)
    member_count: int = attrs.field(default=0)
    thread_metadata: Any = attrs.field(default=None)
    thread_member: Any = attrs.field(alias="member", default=None)
    default_auto_archive_duration: int = attrs.field(default=0)
    permissions: str = attrs.field(default=None)
    flags: int = attrs.field(default=0)
    total_message_sent: int = attrs.field(default=0)
    available_tags: List[Any] = attrs.field(default=None)
    applied_tags: List[Snowflake] = attrs.field(default=None)
    default_reaction_emoji: List[Reaction] = attrs.field(default=None)
    default_thread_rate_limit_per_user: int = attrs.field(default=0)
    default_sort_order: int = attrs.field(default=0)
    default_forum_layout: int = attrs.field(default=0)

    @classmethod
    def as_dict_iter(cls, data):
        if data is not None:
            return [cls(**i) for i in data]
