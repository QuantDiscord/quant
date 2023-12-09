import datetime
from typing import Dict, Any, List

import attrs

from quant.entities.guild import GuildMember
from quant.entities.user import User


class EntityFactory:
    @staticmethod
    def serialize_member(member: GuildMember) -> Dict[str, Any]:
        return attrs.asdict(member)

    @staticmethod
    def deserialize_member(
        username: str | None = None,
        deaf: bool = False,
        mute: bool = False,
        flags: int | None = None,
        pending: bool = False,
        permissions: str | None = None,
        nick: str | None = None,
        avatar: str | None = None,
        roles: List[Any] | None = None,
        joined_at: datetime.datetime | None = None,
        premium_since: int | None = None,
        communication_disabled_until: int | None = None,
        user: User | None = None,
        unusual_dm_activity_until: Any | None = None
    ):
        return GuildMember(
            username=username,
            deaf=deaf,
            mute=mute,
            flags=flags,
            pending=pending,
            permissions=permissions,
            nick=nick,
            avatar=avatar,
            roles=roles,
            joined_at=joined_at,
            premium_since=premium_since,
            communication_disabled_until=communication_disabled_until,
            user=user,
            unusual_dm_activity_until=unusual_dm_activity_until
        )
