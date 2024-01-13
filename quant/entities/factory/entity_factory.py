import datetime
from typing import Dict, Any, List

import attrs

from quant.entities.guild import GuildMember
from quant.entities.user import User
from quant.entities.action_row import ActionRow
from quant.api.entities.component import Component
from quant.entities.snowflake import Snowflake


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
    ) -> GuildMember:
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

    @staticmethod
    def serialize_action_row(row: ActionRow) -> Dict[str, Any] | None:
        if row is None:
            return

        return {
            "type": ActionRow.INTERACTION_TYPE,
            "components": [component.as_json() for component in row.components]
        }

    @staticmethod
    def deserialize_action_row(components: List[Component] | Component) -> ActionRow:
        return ActionRow(components=components)

    @staticmethod
    def serialize_user(user: User) -> Dict[str, Any]:
        return attrs.asdict(user)

    @staticmethod
    def deserialize_user(
        username: str,
        user_id: Snowflake,
        flags: int,
        premium_type: int,
        public_flags: int,
        avatar_decoration_data: Any,
        verified: bool,
        member: Any,
        email: str,
        is_bot: bool,
        is_system: bool,
        mfa_enabled: bool,
        banner_hash: str,
        discriminator: str | None = None,
        display_name: str | None = None,
        global_name: str | None = None,
        avatar: str | None = None,
        accent_color: int | None = None,
        banner_color: int | None = None,
        avatar_decoration: str | None = None,
        locale: str | None = None
    ) -> User:
        return User(
            username=username,
            user_id=user_id,
            flags=flags,
            premium_type=premium_type,
            public_flags=public_flags,
            avatar_decoration_data=avatar_decoration_data,
            verified=verified,
            member=member,
            email=email,
            is_bot=is_bot,
            is_system=is_system,
            mfa_enabled=mfa_enabled,
            banner_hash=banner_hash,
            discriminator=discriminator,
            display_name=display_name,
            global_name=global_name,
            avatar=avatar,
            accent_color=accent_color,
            banner_color=banner_color,
            avatar_decoration=avatar_decoration,
            locale=locale
        )
