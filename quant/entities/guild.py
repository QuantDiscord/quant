"""
MIT License

Copyright (c) 2024 MagM1go

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations

import datetime
import typing
from typing import List, Any, TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from .invite import Invite

from .member import GuildMember
from .user import User
from .channel import Channel
from .voice_state_update import VoiceState
from .model import BaseModel
from .snowflake import Snowflake
from .roles import GuildRole
from .permissions import Permissions


@attrs.define(hash=True)
class Guild(BaseModel):
    id: Snowflake = attrs.field()
    name: str = attrs.field()
    owner_id: Snowflake = attrs.field()
    verification_level: int = attrs.field()
    explicit_content_filter: int = attrs.field()
    default_message_notifications: int = attrs.field()
    mfa_level: int = attrs.field()
    threads: List[Any] = attrs.field()
    stage_instances: List[Any] = attrs.field()
    unavailable: bool = attrs.field()
    embedded_activities: List[Any] = attrs.field()
    channels: List[Channel] = attrs.field()
    guild_scheduled_events: List[Any] = attrs.field()
    guild_hashes: List[Any] = attrs.field()
    lazy: bool = attrs.field()
    application_command_counts: int = attrs.field()
    member_count: int = attrs.field()
    presences: List[Any] = attrs.field()
    members: List[GuildMember] = attrs.field()
    large: bool = attrs.field()
    permissions: Permissions = attrs.field()
    roles: List[GuildRole] = attrs.field()
    emojis: List[Any] = attrs.field()
    icon: str = attrs.field()
    icon_hash: str = attrs.field()
    splash: str = attrs.field()
    discovery_slash: str = attrs.field()
    owner: bool = attrs.field()
    region: str = attrs.field()
    afk_channel_id: int = attrs.field()
    afk_timeout: int = attrs.field()
    widget_enabled: bool = attrs.field()
    widget_channel_id: int = attrs.field()
    features: List[Any] = attrs.field()
    application_id: int = attrs.field()
    system_channel_id: int = attrs.field()
    system_channel_flags: int = attrs.field()
    rules_channel_id: int = attrs.field()
    max_presences: int = attrs.field()
    max_members: int = attrs.field()
    vanity_url_code: str = attrs.field()
    description: str = attrs.field()
    banner: str = attrs.field()
    premium_tier: int = attrs.field()
    premium_subscription_count: int = attrs.field()
    preferred_locale: str = attrs.field()
    public_updates_channel_id: int = attrs.field()
    max_video_channel_users: int = attrs.field()
    max_stage_video_channel_users: int = attrs.field()
    approximate_member_count: int = attrs.field()
    approximate_presence_count: int = attrs.field()
    welcome_screen: Any = attrs.field()
    nsfw_level: int = attrs.field()
    stickers: List[Any] = attrs.field()
    premium_progress_bar_enabled: bool = attrs.field()
    safety_alerts_channel_id: int = attrs.field()
    voice_states: List[VoiceState] = attrs.field()
    home_header: str = attrs.field()
    discovery_splash: str = attrs.field()
    hub_type: int = attrs.field()
    latest_onboarding_question_id: int = attrs.field()
    nsfw: bool = attrs.field()
    incidents_data: str = attrs.field()
    embed_enabled: bool = attrs.field()
    embed_channel_id: int = attrs.field()
    inventory_settings: Any = attrs.field()
    soundboard_sounds: List[Any] = attrs.field()
    version: int = attrs.field()
    locale: str = attrs.field()

    async def delete(self) -> None:
        await self.client.rest.delete_guild(self.id)

    def get_member(self, member_id: Snowflake | int) -> GuildMember:
        return self.client.cache.get_member(self.id, member_id)

    async def fetch_member(self, member_id: Snowflake | int) -> GuildMember:
        return await self.client.rest.fetch_guild_member(guild_id=self.id, user_id=member_id)

    async def fetch_members(self, limit: int = 1000, after: Snowflake | int = Snowflake()) -> List[GuildMember]:
        return await self.client.rest.fetch_guild_members(guild_id=self.id, limit=limit, after=after)

    async def ban(
        self,
        member: Snowflake | int | GuildMember,
        reason: str = None,
        delete_message_days: int = 0,
        delete_message_seconds: int = 0
    ) -> None:
        await self.client.rest.create_guild_ban(
            guild_id=self.id,
            member_id=member.user.id if isinstance(member, GuildMember) else member,
            reason=reason,
            delete_message_days=delete_message_days,
            delete_message_seconds=delete_message_seconds
        )

    async def kick(self, member: Snowflake | int | GuildMember, reason: str | None = None) -> None:
        await self.client.rest.remove_guild_member(
            user_id=member.user.id,
            guild_id=self.id,
            reason=reason
        )

    async def fetch_invites(self) -> List[Invite]:
        return await self.client.rest.fetch_guild_invites(guild_id=self.id)

    def get_role(self, role_id: Snowflake | int) -> GuildRole:
        return self.client.cache.get_role(role_id=role_id)

    def get_channel(self, channel_id: Snowflake | int) -> Channel:
        return self.client.cache.get_channel(channel_id=channel_id)

    async def modify_member(
        self,
        member: Snowflake | int | GuildMember | User,
        nick: str | None = None,
        roles: List[Snowflake | int] | None = None,
        mute: bool | None = None,
        deaf: bool | None = None,
        move_channel_id: Snowflake | int | None = None,
        communication_disabled_until: datetime.datetime | None = None,
        flags: int | None = None,
        reason: str | None = None
    ) -> GuildMember:
        return await self.client.rest.modify_guild_member(
            user_id=member if not isinstance(member, (GuildMember, User)) else member.id,
            guild_id=self.id,
            nick=nick,
            roles=roles,
            mute=mute,
            deaf=deaf,
            move_channel_id=move_channel_id,
            communication_disabled_until=communication_disabled_until,
            flags=flags,
            reason=reason
        )

    def get_everyone_role(self) -> GuildRole:
        return list(filter(lambda r: r.id == self.id, self.roles))[0]
