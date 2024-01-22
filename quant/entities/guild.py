from __future__ import annotations

import datetime
from typing import List, Any, TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from .invite import Invite

from .channel import Channel
from .member import GuildMember
from .voice_state_update import VoiceState
from .model import BaseModel
from .snowflake import Snowflake


@attrs.define
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
    joined_at: datetime.datetime = attrs.field()
    member_count: int = attrs.field()
    presences: List[Any] = attrs.field()
    members: List[GuildMember] = attrs.field()
    large: bool = attrs.field()
    permissions: str = attrs.field()
    roles: List[Any] = attrs.field()
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
        return [i for i in self.members if i.user.id == member_id][0]

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

    async def fetch_invites(self) -> List[Invite]:
        return await self.client.rest.fetch_guild_invites(guild_id=self.id)
