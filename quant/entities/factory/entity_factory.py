import datetime
from typing import Dict, Any, List, Callable

import attrs

from quant.entities.voice_state_update import VoiceState
from quant.entities.interactions.interaction import InteractionData, InteractionType, Interaction
from quant.entities.channel import Channel, Thread, ThreadMetadata, ChannelType, VoiceChannel
from quant.entities.message import Message
from quant.entities.guild import Guild
from quant.entities.guild import GuildMember
from quant.entities.user import User
from quant.entities.emoji import Reaction, PartialReaction
from quant.entities.action_row import ActionRow
from quant.api.entities.component import Component
from quant.entities.snowflake import Snowflake
from quant.utils.json_builder import MutableJsonBuilder
from quant.utils.attrs_extensions import iso_to_datetime


class EntityFactory:
    def __init__(self) -> None:
        self._channel_converter: Dict[ChannelType, Callable] = {
            ChannelType.GUILD_TEXT: self.deserialize_channel,
            ChannelType.GUILD_VOICE: self.deserialize_voice_channel,
            ChannelType.PUBLIC_THREAD: self.deserialize_thread,
            ChannelType.PRIVATE_THREAD: self.deserialize_thread
        }

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

    def deserialize_user(self, payload: MutableJsonBuilder | Dict) -> User:
        return User(
            username=payload.get("username"),
            id=Snowflake(payload.get("id")),
            flags=payload.get("flags", 0),
            premium_type=payload.get("premium_type", 0),
            public_flags=payload.get("public_flags", 0),
            avatar_decoration_data=payload.get("avatar_decoration_data", 0),
            verified=payload.get("verified", False),
            member=self.deserialize_member(**payload.get("member")) if payload.get("member") is not None else None,
            email=payload.get("email"),
            bot=payload.get("bot", False),
            system=payload.get("system", False),
            mfa_enabled=payload.get("mfa_enabled", False),
            banner=payload.get("banner"),
            discriminator=payload.get("discriminator"),
            display_name=payload.get("display_name"),
            global_name=payload.get("global_name"),
            avatar=payload.get("avatar"),
            accent_color=payload.get("accent_color", 0),
            banner_color=payload.get("banner_color", 0),
            avatar_decoration=payload.get("avatar_decoration"),
            locale=payload.get("locale")
        )

    @staticmethod
    def serialize_interaction(interaction: Interaction) -> Dict[str, Any]:
        return attrs.asdict(interaction)

    @staticmethod
    def deserialize_interaction(
        interaction_name: str,
        interaction_id: Snowflake,
        application_id: Snowflake,
        interaction_data: InteractionData,
        guild_id: Snowflake,
        channel: Channel,
        channel_id: Snowflake,
        interaction_token: str,
        guild: Guild,
        interaction_type: InteractionType = InteractionType.PING,
        member: GuildMember | None = None,
        user: User | None = None,
        version: int = -1,
        app_permissions: str | None = None,
        locale: str | None = None,
        guild_locale: str | None = None,
        entitlements: List[Any] | None = None,
        entitlement_sku_ids: Any | None = None,
        message: Message | None = None,
        authorizing_integration_owners: Any | None = None
    ) -> Interaction:
        return Interaction(
            interaction_name=interaction_name,
            interaction_id=interaction_id,
            application_id=application_id,
            interaction_data=interaction_data,
            guild_id=guild_id,
            channel=channel,
            channel_id=channel_id,
            interaction_token=interaction_token,
            guild=guild,
            interaction_type=interaction_type,
            member=member,
            user=user,
            version=version,
            app_permissions=app_permissions,
            locale=locale,
            guild_locale=guild_locale,
            entitlements=entitlements,
            entitlement_sku_ids=entitlement_sku_ids,
            message=message,
            authorizing_integration_owners=authorizing_integration_owners
        )

    def deserialize_voice_state(self, payload: MutableJsonBuilder | Dict) -> VoiceState:
        return VoiceState(
            guild_id=Snowflake(payload.get("guild_id")),
            channel_id=Snowflake(payload.get("channel_id")),
            user_id=Snowflake(payload.get("user_id")),
            member=self.deserialize_member(**payload.get("member")) if payload.get("member") is not None else None,
            session_id=payload.get("session_id"),
            deaf=payload.get("deaf", False),
            mute=payload.get("mute", False),
            self_deaf=payload.get("self_deaf", False),
            self_mute=payload.get("self_mute", False),
            self_stream=payload.get("self_stream", False),
            self_video=payload.get("self_video", False),
            suppress=payload.get("suppress", False),
            request_to_speak_timestamp=iso_to_datetime(payload.get("request_to_speak_timestamp"))
        )

    def deserialize_thread(self, payload: MutableJsonBuilder | Dict) -> Thread:
        return Thread(
            id=Snowflake(payload.get("id", 0)),
            type=ChannelType(payload.get("type", 0)),
            guild_id=Snowflake(payload.get("guild_id", 0)),
            position=payload.get("position", 0),
            permission_overwrites=payload.get("permission_overwrites"),
            name=payload.get("name"),
            topic=payload.get("topic"),
            nsfw=payload.get("nsfw", False),
            version=payload.get("version"),
            status=payload.get("status"),
            theme_color=payload.get("theme_color"),
            icon_emoji=payload.get("icon_emoji"),
            template=payload.get("template"),
            last_message_id=Snowflake(payload.get("last_message_id", 0)),
            rate_limit_per_user=payload.get("rate_limit_per_user", 0),
            recipients=[self.deserialize_user(**user_data) for user_data in payload.get("recipients", [])],
            icon=payload.get("icon", None),
            owner_id=Snowflake(payload.get("owner_id", 0)),
            application_id=Snowflake(payload.get("application_id", 0)),
            managed=payload.get("managed", False),
            parent_id=Snowflake(payload.get("parent_id", 0)),
            last_pin_timestamp=iso_to_datetime(payload.get("last_pin_timestamp")),
            message_count=payload.get("message_count", 0),
            member_count=payload.get("member_count", 0),
            thread_metadata=self._deserialize_thread_metadata(payload.get("thread_metadata")),
            member=payload.get("member"),
            default_auto_archive_duration=payload.get("default_auto_archive_duration", 0),
            permissions=payload.get("permissions"),
            flags=payload.get("flags", 0),
            total_message_sent=payload.get("total_message_sent", 0),
            available_tags=payload.get("available_tags"),
            applied_tags=[Snowflake(tag) for tag in payload.get("applied_tags", [])],
            default_reaction_emoji=[Reaction(emoji=reaction_data) for reaction_data in
                                    payload.get("default_reaction_emoji", [])],
            default_thread_rate_limit_per_user=payload.get("default_thread_rate_limit_per_user", 0),
            default_sort_order=payload.get("default_sort_order", 0),
            default_forum_layout=payload.get("default_forum_layout", 0)
        )

    @staticmethod
    def deserialize_channel(payload: MutableJsonBuilder | Dict) -> Channel:
        return Channel(
            id=Snowflake(payload.get("id", 0)),
            type=ChannelType(payload.get("type", 0)),
            guild_id=Snowflake(payload.get("guild_id", 0)),
            position=payload.get("position", 0),
            permission_overwrites=payload.get("permission_overwrites"),
            name=payload.get("name"),
            topic=payload.get("topic"),
            nsfw=payload.get("nsfw", False),
            version=payload.get("version"),
            status=payload.get("status"),
            theme_color=payload.get("theme_color"),
            icon_emoji=payload.get("icon_emoji"),
            template=payload.get("template"),
            last_message_id=Snowflake(payload.get("last_message_id", 0)),
            rate_limit_per_user=payload.get("rate_limit_per_user", 0),
            icon=payload.get("icon", None),
            owner_id=Snowflake(payload.get("owner_id", 0)),
            application_id=Snowflake(payload.get("application_id", 0)),
            managed=payload.get("managed", False),
            parent_id=Snowflake(payload.get("parent_id", 0)),
            last_pin_timestamp=iso_to_datetime(payload.get("last_pin_timestamp")),
            message_count=payload.get("message_count", 0),
            member=payload.get("member"),
            permissions=payload.get("permissions"),
            flags=payload.get("flags", 0),
            total_message_sent=payload.get("total_message_sent", 0),
            default_reaction_emoji=[Reaction(emoji=reaction_data) for reaction_data in
                                    payload.get("default_reaction_emoji", [])],
            default_thread_rate_limit_per_user=payload.get("default_thread_rate_limit_per_user", 0),
            default_sort_order=payload.get("default_sort_order", 0),
            default_forum_layout=payload.get("default_forum_layout", 0)
        )

    @staticmethod
    def deserialize_voice_channel(payload: MutableJsonBuilder | Dict) -> VoiceChannel:
        return VoiceChannel(
            id=Snowflake(payload.get("id", 0)),
            type=ChannelType(payload.get("type", 0)),
            guild_id=Snowflake(payload.get("guild_id", 0)),
            position=payload.get("position", 0),
            permission_overwrites=payload.get("permission_overwrites"),
            name=payload.get("name"),
            topic=payload.get("topic"),
            nsfw=payload.get("nsfw", False),
            version=payload.get("version"),
            status=payload.get("status"),
            theme_color=payload.get("theme_color"),
            icon_emoji=payload.get("icon_emoji"),
            template=payload.get("template"),
            last_message_id=Snowflake(payload.get("last_message_id", 0)),
            rate_limit_per_user=payload.get("rate_limit_per_user", 0),
            icon=payload.get("icon", None),
            owner_id=Snowflake(payload.get("owner_id", 0)),
            application_id=Snowflake(payload.get("application_id", 0)),
            managed=payload.get("managed", False),
            parent_id=Snowflake(payload.get("parent_id", 0)),
            last_pin_timestamp=iso_to_datetime(payload.get("last_pin_timestamp")),
            message_count=payload.get("message_count", 0),
            member=payload.get("member"),
            permissions=payload.get("permissions"),
            flags=payload.get("flags", 0),
            total_message_sent=payload.get("total_message_sent", 0),
            default_reaction_emoji=[Reaction(emoji=reaction_data) for reaction_data in
                                    payload.get("default_reaction_emoji", [])],
            default_thread_rate_limit_per_user=payload.get("default_thread_rate_limit_per_user", 0),
            default_sort_order=payload.get("default_sort_order", 0),
            default_forum_layout=payload.get("default_forum_layout", 0),
            bitrate=int(payload.get("bitrate", 0)),
            user_limit=int(payload.get("user_limit", 0)),
            rtc_region=payload.get("rtc_region"),
            video_quality_mode=int(payload.get("video_quality_mode", 0))
        )

    def deserialize_reaction(self, payload: MutableJsonBuilder | Dict) -> Reaction:
        return Reaction(
            user_id=Snowflake(payload.get("user_id")),
            reaction_type=payload.get("reaction_type"),
            message_id=Snowflake(payload.get("message_id")),
            message_author_id=Snowflake(payload.get("message_author_id")),
            member=self.deserialize_member(**payload.get("member")) if payload.get("member") is not None else None,
            emoji=PartialReaction(**payload.get("emoji")) if payload.get("emoji") is not None else None,
            channel_id=Snowflake(payload.get("channel_id")),
            burst=payload.get("burst", False),
            guild_id=Snowflake(payload.get("guild_id")),
            burst_colors=payload.get("burst_colors")
        )

    def deserialize_guild(self, payload: MutableJsonBuilder | Dict) -> Guild:
        return Guild(
            id=Snowflake(payload["id"]),
            name=payload.get("name"),
            owner_id=Snowflake(payload.get("owner_id")),
            verification_level=payload.get("verification_level", 0),
            explicit_content_filter=payload.get("explicit_content_filter", 0),
            default_message_notifications=payload.get("default_message_notifications", 0),
            mfa_level=payload.get("mfa_level", 0),
            threads=[self.deserialize_thread(thread_data) for thread_data in payload.get("threads", [])],
            stage_instances=payload.get("stage_instances", []),
            unavailable=payload.get("unavailable", False),
            embedded_activities=payload.get("embedded_activities", []),
            channels=[self._channel_converter.get(ChannelType(channel_data["type"]),
                                                  self._channel_converter[ChannelType.GUILD_TEXT])(channel_data)
                      for channel_data in payload.get("channels", [])],
            guild_scheduled_events=payload.get("guild_scheduled_events", []),
            guild_hashes=payload.get("guild_hashes", []),
            lazy=payload.get("lazy", False),
            application_command_counts=payload.get("application_command_counts", 0),
            joined_at=payload.get("joined_at", None),
            member_count=payload.get("member_count", 0),
            presences=payload.get("presences", []),
            members=[self.deserialize_member(**member_data) for member_data in payload.get("members", [])],
            large=payload.get("large", False),
            permissions=payload.get("permissions", None),
            roles=payload.get("roles", []),
            emojis=payload.get("emojis", []),
            icon=payload.get("icon", None),
            icon_hash=payload.get("icon_hash", None),
            splash=payload.get("splash", None),
            discovery_slash=payload.get("discovery_slash", None),
            owner=payload.get("owner", False),
            region=payload.get("region", None),
            afk_channel_id=payload.get("afk_channel_id", 0),
            afk_timeout=payload.get("afk_timeout", 0),
            widget_enabled=payload.get("widget_enabled", False),
            widget_channel_id=payload.get("widget_channel_id", 0),
            features=payload.get("features", []),
            application_id=payload.get("application_id", 0),
            system_channel_id=payload.get("system_channel_id", 0),
            system_channel_flags=payload.get("system_channel_flags", 0),
            rules_channel_id=payload.get("rules_channel_id", 0),
            max_presences=payload.get("max_presences", None),
            max_members=payload.get("max_members", 0),
            vanity_url_code=payload.get("vanity_url_code", None),
            description=payload.get("description", None),
            banner=payload.get("banner", None),
            premium_tier=payload.get("premium_tier", 0),
            premium_subscription_count=payload.get("premium_subscription_count", 0),
            preferred_locale=payload.get("preferred_locale", None),
            public_updates_channel_id=payload.get("public_updates_channel_id", 0),
            max_video_channel_users=payload.get("max_video_channel_users", 0),
            max_stage_video_channel_users=payload.get("max_stage_video_channel_users", 0),
            approximate_member_count=payload.get("approximate_member_count", 0),
            approximate_presence_count=payload.get("approximate_presence_count", 0),
            welcome_screen=payload.get("welcome_screen", None),
            nsfw_level=payload.get("nsfw_level", 0),
            stickers=payload.get("stickers", []),
            premium_progress_bar_enabled=payload.get("premium_progress_bar_enabled", False),
            safety_alerts_channel_id=payload.get("safety_alerts_channel_id", 0),
            voice_states=[self.deserialize_voice_state(voice_state_data) for voice_state_data in
                          payload.get("voice_states", [])],
            home_header=payload.get("home_header", None),
            discovery_splash=payload.get("discovery_splash", None),
            hub_type=payload.get("hub_type", 0),
            latest_onboarding_question_id=payload.get("latest_onboarding_question_id", 0),
            nsfw=payload.get("nsfw", False),
            incidents_data=payload.get("incidents_data", None),
            embed_enabled=payload.get("embed_enabled", False),
            embed_channel_id=payload.get("embed_channel_id", 0),
            inventory_settings=payload.get("inventory_settings", None),
            soundboard_sounds=payload.get("soundboard_sounds", []),
            version=payload.get("version", 0),
            locale=payload.get("locale", None),
        )

    @staticmethod
    def _deserialize_thread_metadata(payload: MutableJsonBuilder | Dict) -> ThreadMetadata:
        return ThreadMetadata(
            archived=payload.get("archived", False),
            auto_archive_duration=payload.get("auto_archive_duration", 0),
            archive_timestamp=iso_to_datetime(payload.get("archive_timestamp")),
            locked=payload.get("locked", False),
            invitable=payload.get("invitable", False),
            create_timestamp=iso_to_datetime(payload.get("create_timestamp"))
        )
