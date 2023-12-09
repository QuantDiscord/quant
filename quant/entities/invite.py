import enum
import datetime
from typing import Any

import attrs

from .guild import Guild
from .channel import Channel
from .user import User
from quant.utils.attrs_extensions import execute_converters


class InviteTargetType(enum.Enum):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Invite:
    code: str
    guild: Guild | None = attrs.field(default=None, converter=Guild.as_dict)
    channel: Channel | None = attrs.field(default=None, converter=Channel.as_dict)
    inviter: User | None = attrs.field(default=None, converter=User.as_dict)
    target_type: int | None = attrs.field(default=0)
    target_application: InviteTargetType | None = attrs.field(default=None, converter=InviteTargetType)
    approximate_presence_count: int | None = attrs.field(default=0)
    approximate_member_count: int | None = attrs.field(default=0)
    expires_at: datetime.datetime | None = attrs.field(default=None)
    stage_instance: Any | None = attrs.field(default=None)
    guild_scheduled_event: Any | None = attrs.field(default=None)
