from typing import List, Any

import attrs


@attrs.define
class GuildMember:
    deaf: bool = attrs.field(default=False)
    mute: bool = attrs.field(default=False)
    flags: int = attrs.field(default=0)
    pending: bool = attrs.field(default=False)
    permissions: str | None = attrs.field(default=None)
    user: Any | None = attrs.field(default=None)
    nick: str | None = attrs.field(default=None)
    avatar: str | None = attrs.field(default=None)
    roles: List[Any] | None = attrs.field(default=None)
    join_time: int = attrs.field(alias="joined_at", default=0)
    premium_since: int | None = attrs.field(default=0)
    communication_disabled_until: int | None = attrs.field(default=0)

    @classmethod
    def from_dict(cls, data):
        if data is not None:
            return cls(**data)
