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

from typing import Dict, Any, TYPE_CHECKING, Callable, List

import attrs

if TYPE_CHECKING:
    from quant.utils.cache.cache_manager import CacheManager
    from quant.entities.button import Button
    from quant.entities.action_row import ActionRow

from quant.impl.files import AttachableURL, File
from quant.impl.core.commands import (
    ApplicationCommandObject,
    ApplicationCommandTypes,
    ApplicationCommandContexts
)
from quant.entities.message import Message, Attachment, MessageFlags
from quant.entities.embeds import Embed, EmbedField, EmbedAuthor, EmbedImage, EmbedThumbnail, EmbedFooter
from quant.entities.voice_state_update import VoiceState
from quant.entities.voice_server_update import VoiceServer
from quant.entities.invite import Invite, _InviteMetadata, InviteTargetType
from quant.entities.modal.modal import ModalInteractionCallbackData
from quant.entities.modal.text_input import TextInput, TextInputStyle
from quant.entities.interactions.interaction import (
    InteractionData, InteractionType, Interaction, InteractionDataOption, InteractionCallbackData
)
from quant.entities.channel import Channel, Thread, ThreadMetadata, ChannelType, VoiceChannel, TextChannel
from quant.entities.guild import Guild
from quant.entities.guild import GuildMember
from quant.entities.roles import GuildRole
from quant.entities.user import User
from quant.entities.emoji import Reaction, PartialReaction, Emoji
from quant.entities.interactions.slash_option import SlashOptionType, ApplicationCommandOption
from quant.entities.interactions.component_types import ComponentType
from quant.entities.snowflake import Snowflake
from quant.entities.integration import IntegrationTypes
from quant.entities.poll import Poll, PollAnswer
from quant.utils.parser import iso_to_datetime, parse_permissions
from quant.entities.permissions import Permissions


class EntityFactory:
    def __init__(self, cache: CacheManager) -> None:
        self._channel_converter: Dict[ChannelType, Callable] = {
            ChannelType.GUILD_TEXT: self.deserialize_text_channel,
            ChannelType.GUILD_VOICE: self.deserialize_voice_channel,
            ChannelType.PUBLIC_THREAD: self.deserialize_thread,
            ChannelType.PRIVATE_THREAD: self.deserialize_thread,
        }
        self.cache = cache

    @staticmethod
    def serialize_member(member: GuildMember) -> Dict[str, Any]:
        return attrs.asdict(member)

    def deserialize_member(
        self,
        payload: Dict,
        guild_id: Snowflake | int | None = None
    ) -> GuildMember:
        if (roles := payload.get("roles")) is not None:
            roles = [self.cache.get_role(Snowflake(role)) for role in roles]

        if (user := payload.get("user")) is not None:
            user = self.deserialize_user(user)

        return GuildMember(
            user=user,
            guild_id=guild_id,
            deaf=payload.get("deaf", False),
            mute=payload.get("mute", False),
            flags=payload.get("flags", 0),
            pending=payload.get("pending"),
            permissions=parse_permissions(int(payload.get("permissions", 0))),
            nick=payload.get("nick"),
            avatar=payload.get("avatar"),
            roles=roles,
            joined_at=iso_to_datetime(payload.get("joined_at")),
            premium_since=payload.get("premium_since", 0),
            communication_disabled_until=payload.get("communication_disabled_until", 0),
            unusual_dm_activity_until=payload.get("unusual_dm_activity_until")
        )

    @staticmethod
    def serialize_application_command(command: ApplicationCommandObject) -> Dict[str, Any] | None:
        if command is None:
            return

        body = {"name": command.name, "description": command.description}

        if command.guild_id is not None and not isinstance(command.guild_id, tuple):
            body["guild_id"] = command.guild_id

        if command.options is not None:
            body["options"] = command.options

        if command.integration_types is not None:
            body["integration_types"] = command.integration_types

        if command.contexts is not None:
            body["contexts"] = command.contexts

        if command.name_localizations is not None:
            body["name_localizations"] = command.name_localizations

        if command.description_localizations is not None:
            body["description_localizations"] = command.description_localizations

        if command.dm_permissions:
            body["dm_permissions"] = command.dm_permissions

        if command.default_member_permissions is not None and not isinstance(command.default_member_permissions, tuple):
            body["default_member_permissions"] = command.default_member_permissions.value

        if command.nsfw is not None:
            body["nsfw"] = command.nsfw

        return body

    def serialize_action_row(self, row: ActionRow) -> Dict[str, Any] | None:
        from quant.entities.button import Button
        from quant.entities.action_row import ActionRow

        components = []
        for component in row.components:
            if isinstance(component, Button):
                component = self.serialize_button(component)
            else:
                component = attrs.asdict(component)

            components.append(component)

        return {
            "type": ActionRow.INTERACTION_TYPE,
            "components": components
        }

    @staticmethod
    def serialize_button(button: Button) -> Dict[str, Any] | None:
        return {
            "type": button.BUTTON_COMPONENT_TYPE,
            "custom_id": button.custom_id,
            "label": button.label,
            "style": button.style.value,
            "emoji": button.emoji,
            "url": button.url,
            "disabled": button.disabled
        }

    def deserialize_action_row(self, payload: Dict | list) -> ActionRow:
        from quant.entities.action_row import ActionRow

        if isinstance(payload, list):
            return ActionRow(components=[self._deserialize_component(component) for component in payload])

        return ActionRow(components=[self._deserialize_component(component) for component in payload.get("components")])

    @staticmethod
    def serialize_user(user: User) -> Dict[str, Any]:
        return attrs.asdict(user)

    def deserialize_user(self, payload: Dict | None) -> User | None:
        if payload is None:
            return

        return User(
            username=payload.get("username"),
            id=Snowflake(payload.get("id")),
            flags=payload.get("flags", 0),
            premium_type=payload.get("premium_type", 0),
            public_flags=payload.get("public_flags", 0),
            avatar_decoration_data=payload.get("avatar_decoration_data", 0),
            verified=payload.get("verified", False),
            member=self.deserialize_member(payload.get("member")) if payload.get("member") is not None else None,
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

    def deserialize_interaction(self, payload: Dict | None) -> Interaction | None:
        if payload is None:
            return

        if (user := payload.get("user")) is not None:
            user = self.deserialize_user(user)

        if (member := payload.get("member")) is not None:
            member = self.deserialize_member(member, Snowflake(payload.get("guild_id")))

        if (channel := payload.get("channel")) is not None:
            channel = self._channel_converter.get(ChannelType(channel["type"]), self.deserialize_channel)(channel)

        return Interaction(
            name=payload.get("name"),
            id=Snowflake(payload.get("id", 0)),
            application_id=Snowflake(payload.get("application_id")),
            data=self._deserialize_interaction_data(payload.get("data")),
            guild_id=Snowflake(payload.get("guild_id")),
            channel=channel,
            channel_id=Snowflake(payload.get("channel_id")),
            token=payload.get("token"),
            type=InteractionType(payload.get("type", InteractionType.PING.value)),
            member=member,
            user=user,
            version=payload.get("version", -1),
            app_permissions=payload.get("app_permissions"),
            locale=payload.get("locale"),
            guild_locale=payload.get("guild_locale"),
            entitlements=payload.get("entitlements"),
            entitlement_sku_ids=payload.get("entitlement_sku_ids"),
            message=self.deserialize_message(payload.get("message")),
            authorizing_integration_owners=payload.get("authorizing_integration_owners")
        )

    def deserialize_voice_state(self, payload: Dict) -> VoiceState:
        return VoiceState(
            guild_id=Snowflake(payload.get("guild_id", 0)),
            channel_id=Snowflake(payload.get("channel_id", 0)),
            user_id=Snowflake(payload.get("user_id", 0)),
            member=self.deserialize_member(payload.get("member"), Snowflake(payload.get("guild_id", 0))) if payload.get("member") is not None else None,
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

    @staticmethod
    def deserialize_voice_server(payload: Dict) -> VoiceServer:
        return VoiceServer(
            token=payload.get("token"),
            guild_id=Snowflake(payload.get("guild_id")),
            endpoint=payload.get("endpoint")
        )

    def deserialize_thread(self, payload: Dict | None) -> Thread | None:
        if payload is None:
            return

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
            recipients=[self.deserialize_user(user_data) for user_data in payload.get("recipients", [])],
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
            permissions=parse_permissions(int(payload.get("permissions", 0))),
            flags=payload.get("flags", 0),
            total_message_sent=payload.get("total_message_sent", 0),
            available_tags=payload.get("available_tags"),
            applied_tags=[Snowflake(tag) for tag in payload.get("applied_tags", [])],
            default_thread_rate_limit_per_user=payload.get("default_thread_rate_limit_per_user", 0),
            default_sort_order=payload.get("default_sort_order", 0)
        )

    def deserialize_text_channel(self, payload: Dict | None) -> TextChannel | None:
        if payload is None:
            return

        return TextChannel(
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
            icon=payload.get("icon", None),
            owner_id=Snowflake(payload.get("owner_id", 0)),
            application_id=Snowflake(payload.get("application_id", 0)),
            managed=payload.get("managed", False),
            parent_id=Snowflake(payload.get("parent_id", 0)),
            member=payload.get("member"),
            permissions=parse_permissions(int(payload.get("permissions", 0))),
            flags=payload.get("flags", 0),
            default_thread_rate_limit_per_user=payload.get("default_thread_rate_limit_per_user", 0),
            default_sort_order=payload.get("default_sort_order", 0),
            last_message_id=Snowflake(payload.get("last_message_id", 0)),
            rate_limit_per_user=payload.get("rate_limit_per_user", 0),
            last_pin_timestamp=iso_to_datetime(payload.get("last_pin_timestamp")),
        )

    def deserialize_channel(self, payload: Dict | None) -> Channel | None:
        if payload is None:
            return

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
            icon=payload.get("icon", None),
            owner_id=Snowflake(payload.get("owner_id", 0)),
            application_id=Snowflake(payload.get("application_id", 0)),
            managed=payload.get("managed", False),
            parent_id=Snowflake(payload.get("parent_id", 0)),
            member=payload.get("member"),
            permissions=parse_permissions(int(payload.get("permissions", 0))),
            flags=payload.get("flags", 0),
            default_thread_rate_limit_per_user=payload.get("default_thread_rate_limit_per_user", 0),
            default_sort_order=payload.get("default_sort_order", 0)
        )

    def deserialize_voice_channel(self, payload: Dict) -> VoiceChannel:
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
            icon=payload.get("icon", None),
            owner_id=Snowflake(payload.get("owner_id", 0)),
            application_id=Snowflake(payload.get("application_id", 0)),
            managed=payload.get("managed", False),
            parent_id=Snowflake(payload.get("parent_id", 0)),
            member=payload.get("member"),
            permissions=parse_permissions(int(payload.get("permissions", 0))),
            flags=payload.get("flags", 0),
            default_thread_rate_limit_per_user=payload.get("default_thread_rate_limit_per_user", 0),
            default_sort_order=payload.get("default_sort_order", 0),
            bitrate=int(payload.get("bitrate", 0)),
            user_limit=int(payload.get("user_limit", 0)),
            rtc_region=payload.get("rtc_region"),
            video_quality_mode=int(payload.get("video_quality_mode", 0))
        )

    def deserialize_emoji(self, payload: Dict) -> Emoji:
        if (roles := payload.get("roles")) is not None:
            roles = [self.cache.get_role(role) for role in roles]

        return Emoji(
            id=Snowflake(payload.get("id", 0)),
            name=payload.get("name"),
            roles=roles,
            user=payload.get("user"),
            require_colons=payload.get("require_colons", False),
            managed=payload.get("managed", False),
            animated=payload.get("animated", False),
            available=payload.get("available", False),
            version=payload.get("version", 0)
        )

    def deserialize_reaction(self, payload: Dict) -> Reaction:
        return Reaction(
            user_id=Snowflake(payload.get("user_id")),
            type=payload.get("reaction_type"),
            message_id=Snowflake(payload.get("message_id")),
            message_author_id=Snowflake(payload.get("message_author_id")),
            member=self.deserialize_member(payload.get("member"), Snowflake(payload.get("guild_id"))) if payload.get("member") is not None else None,
            emoji=PartialReaction(**payload.get("emoji")) if payload.get("emoji") is not None else None,
            channel_id=Snowflake(payload.get("channel_id")),
            burst=payload.get("burst", False),
            guild_id=Snowflake(payload.get("guild_id")),
            burst_colors=payload.get("burst_colors")
        )

    @staticmethod
    def deserialize_role(payload: Dict) -> GuildRole:
        return GuildRole(
            id=Snowflake(payload.get("id", 0)),
            name=payload.get("name"),
            color=payload.get("color"),
            hoist=payload.get("hoist", False),
            icon=payload.get("icon"),
            unicode_emoji=payload.get("unicode_emoji"),
            position=payload.get("position"),
            permissions=parse_permissions(int(payload.get("permissions", -1))),
            managed=payload.get("managed", False),
            mentionable=payload.get("mentionable", False),
            tags=payload.get("tags"),
            flags=payload.get("flags")
        )

    @staticmethod
    def deserialize_embed(payload: Dict) -> Embed:
        if (footer := payload.get("footer")) is not None:
            footer = EmbedFooter(**footer)

        if (image := payload.get("image")) is not None:
            image = EmbedImage(**image)

        if (thumbnail := payload.get("thumbnail")) is not None:
            thumbnail = EmbedThumbnail(**thumbnail)

        if (author := payload.get("author")) is not None:
            author = EmbedAuthor("author")

        if (fields := payload.get("fields")) is not None:
            fields = [EmbedField(**field) for field in fields]

        return Embed(
            title=payload.get("title"),
            description=payload.get("description"),
            url=payload.get("url"),
            timestamp=payload.get("timestamp"),
            color=payload.get("color"),
            footer=footer,
            image=image,
            author=author,
            thumbnail=thumbnail,
            fields=fields
        )

    @staticmethod
    def serialize_embed(embed: Embed) -> Dict:
        return attrs.asdict(embed)

    @staticmethod
    def serialize_attachment(index: int, attachment: Attachment | AttachableURL | File) -> Dict | None:
        if isinstance(attachment, AttachableURL | File):
            return {
                "id": index,
                "filename": f"file_{index}_{attachment.filename}",
                "url": str(attachment.url)
            }

        return attrs.asdict(attachment)

    def deserialize_application_command(self, payload: Dict) -> ApplicationCommandObject:
        if (options := payload.get("options")) is not None:
            options = [self.deserialize_slash_option(option) for option in options]

        if (integration_types := payload.get("integration_types")) is not None:
            integration_types = [IntegrationTypes(i_type) for i_type in integration_types]

        if (contexts := payload.get("contexts")) is not None:
            contexts = [ApplicationCommandContexts(context) for context in contexts]

        return ApplicationCommandObject(
            cmd_id=Snowflake(payload.get("id")),
            cmd_type=ApplicationCommandTypes(payload.get("type")),
            application_id=Snowflake(payload.get("application_id", 0)),
            guild_id=Snowflake(payload.get("guild_id", 0)),
            name=payload.get("name"),
            description=payload.get("description"),
            options=options,
            default_member_permissions=parse_permissions(payload.get("default_member_permissions")),
            dm_permissions=payload.get("dm_permissions"),
            nsfw=payload.get("nsfw", False),
            integration_types=integration_types,
            contexts=contexts
        )

    def deserialize_message(self, payload: Dict | None) -> Message | None:
        if payload is None:
            return

        if (embeds := payload.get("embeds")) is not None:
            embeds = [self.deserialize_embed(embed) for embed in embeds]

        if (member := payload.get("member")) is not None:
            member = self.deserialize_member(member, Snowflake(payload.get("guild_id", 0)))

        if (attachments := payload.get("attachments")) is not None:
            attachments = [self.deserialize_attachment(attachment) for attachment in attachments]

        return Message(
            type=payload.get("type"),
            timestamp=iso_to_datetime(payload.get("timestamp")),
            channel_id=Snowflake(payload.get("channel_id", 0)),
            position=payload.get("position", 0),
            id=Snowflake(payload.get("id", 0)),
            guild_id=Snowflake(payload.get("guild_id", 0)),
            member=member,
            author=self.deserialize_user(payload.get("author")),
            content=payload.get("content"),
            nonce=payload.get("nonce"),
            tts=payload.get("tts"),
            embeds=embeds,
            edited_timestamp=payload.get("edited_timestamp"),
            mention_everyone=payload.get("mention_everyone"),
            mentions=payload.get("mentions"),
            mention_roles=payload.get("mention_roles"),
            mention_channels=payload.get("mention_channels"),
            message_reference=payload.get("message_reference"),
            components=payload.get("components"),
            stickers=payload.get("stickers"),
            attachments=attachments,
            flags=payload.get("flags", 0),
            referenced_message=payload.get("referenced_message"),
            pinned=payload.get("pinned"),
            webhook_id=Snowflake(payload.get("webhook_id", 0)),
            activity=payload.get("activity"),
            application=payload.get("application"),
            application_id=Snowflake(payload.get("application_id", 0)),
            interaction=self.deserialize_interaction(payload.get("interaction")),
            thread=self.deserialize_thread(payload.get("thread")),
            sticker_items=payload.get("sticker_items"),
            role_subscription_data=payload.get("role_subscription_data"),
            resolved=payload.get("resolved", False)
        )

    @staticmethod
    def deserialize_attachment(payload: Dict) -> Attachment:
        return Attachment(
            id=Snowflake(payload.get("id", 0)),
            filename=payload.get("filename"),
            description=payload.get("description"),
            content_type=payload.get("content_type"),
            size=payload.get("size", 0),
            url=payload.get("url"),
            proxy_url=payload.get("proxy_url"),
            height=payload.get("height"),
            width=payload.get("width"),
            ephemeral=payload.get("ephemeral", False),
            duration_secs=payload.get("duration_secs", float(0)),
            waveform=payload.get("waveform"),
            flags=payload.get("flags", 0)
        )

    def serialize_interaction_callback_data(
        self,
        callback_data: InteractionCallbackData
    ) -> Dict:
        flags = callback_data.flags

        if isinstance(flags, MessageFlags):
            flags = flags.value

        if (embeds := callback_data.embeds) is not None:
            embeds = [self.serialize_embed(embed) for embed in embeds]

        if (components := callback_data.components) is not None:
            components = [self.serialize_action_row(components)]

        if (allowed_mentions := callback_data.allowed_mentions) is not None:
            allowed_mentions = attrs.asdict(allowed_mentions)

        if (attachments := callback_data.attachments) is not None:
            attachments = [self.serialize_attachment(index, attachment) for index, attachment in enumerate(attachments)]

        return {
            "tts": callback_data.tts,
            "content": callback_data.content,
            "embeds": embeds,
            "allowed_mentions": allowed_mentions,
            "flags": flags,
            "components": components,
            "attachments": attachments
        }

    def serialize_modal_interaction_callback_data(self, callback_data: ModalInteractionCallbackData) -> Dict:
        return {
            "title": callback_data.title,
            "custom_id": callback_data.custom_id,
            "components": [self.serialize_action_row(row) for row in callback_data.components]
        }

    def deserialize_interaction_callback_data(self, payload: Dict) -> InteractionCallbackData:
        if (embeds := payload.get("embeds")) is not None:
            embeds = [self.deserialize_embed(embed) for embed in embeds]

        if (attachments := payload.get("attachments")) is not None:
            attachments = [self.deserialize_attachment(attachment) for attachment in attachments]

        return InteractionCallbackData(
            tts=payload.get("tts", False),
            content=payload.get("content"),
            embeds=embeds,
            allowed_mentions=payload.get("allowed_mentions"),
            flags=payload.get("flags"),
            components=self.deserialize_action_row(payload.get("components")),
            attachments=attachments
        )

    @staticmethod
    def deserialize_text_input(payload: Dict) -> TextInput:
        return TextInput(
            custom_id=payload.get("custom_id"),
            style=TextInputStyle(payload.get("style", 0)),
            label=payload.get("label", None),
            min_length=payload.get("min_length", 0),
            max_length=payload.get("max_length", 4000),
            required=payload.get("required", False),
            value=payload.get("value", None),
            placeholder=payload.get("placeholder", None)
        )

    def deserialize_slash_option(self, payload: Dict) -> ApplicationCommandOption:
        if (options := payload.get("options")) is not None:
            options = [self.deserialize_slash_option(option) for option in options]

        return ApplicationCommandOption(
            name=payload.get("name"),
            description=payload.get("description"),
            min_value=payload.get("min_value"),
            max_value=payload.get("max_value"),
            min_length=payload.get("min_length"),
            max_length=payload.get("max_length"),
            autocomplete=payload.get("autocomplete"),
            channel_types=payload.get("channel_types"),
            options=options,
            choices=payload.get("choices"),
            required=payload.get("required"),
            type=payload.get("type")
        )

    def serialize_slash_option(self, option: ApplicationCommandOption) -> Dict:
        body = {}

        if (options := option.options) is not None:
            options = [self.serialize_slash_option(opt) for opt in options]

        body["name"] = option.name.lower()
        body["description"] = option.description
        body["min_value"] = option.min_value
        body["max_value"] = option.max_value
        body["min_length"] = option.min_length
        body["max_length"] = option.max_length
        body["autocomplete"] = option.autocomplete
        body["channel_types"] = option.channel_types
        body["options"] = options
        body["choices"] = option.choices
        body["required"] = option.required

        if option.type is not None:
            body["type"] = option.type.value
        else:
            body["type"] = SlashOptionType.STRING.value

        return body

    def deserialize_guild(self, payload: Dict | None) -> Guild | None:
        if payload is None:
            return

        channels = [self._channel_converter.get(ChannelType(c["type"]), self.deserialize_channel)(c)
                    for c in payload.get("channels", [])]
        roles = [self.deserialize_role(role) for role in payload.get("roles", [])]
        emojis = [self.deserialize_emoji(emoji) for emoji in payload.get("emojis", [])]

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
            channels=channels,
            guild_scheduled_events=payload.get("guild_scheduled_events", []),
            guild_hashes=payload.get("guild_hashes", []),
            lazy=payload.get("lazy", False),
            application_command_counts=payload.get("application_command_counts", 0),
            member_count=payload.get("member_count", 0),
            presences=payload.get("presences", []),
            members=[],
            large=payload.get("large", False),
            permissions=parse_permissions(int(payload.get("permissions", 0))),
            roles=roles,
            emojis=emojis,
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
            max_presences=payload.get("max_presences", 0),
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

    def deserialize_invite(self, payload: Dict) -> Invite:
        if (guild := payload.get("guild")) is not None:
            guild = self.deserialize_guild(guild)

        if (channel := payload.get("channel")) is not None:
            channel = self.deserialize_guild(channel)

        if (inviter := payload.get("inviter")) is not None:
            inviter = self.deserialize_user(inviter)

        if (target_user := payload.get("target_user")) is not None:
            target_user = self.deserialize_user(target_user)

        return Invite(
            code=payload.get("code"),
            guild_id=Snowflake(payload.get("guild_id", 0)),
            guild=guild,
            channel=channel,
            inviter=inviter,
            target_type=InviteTargetType(payload.get("target_type", 0)),
            target_user=target_user,
            target_application=payload.get("target_application"),
            approximate_presence_count=payload.get("approximate_presence_count", 0),
            approximate_member_count=payload.get("approximate_member_count", 0),
            expires_at=iso_to_datetime(payload.get("expires_at")),
            stage_instance=payload.get("stage_instance"),
            guild_scheduled_event=payload.get("guild_scheduled_event"),
            metadata=self._deserialize_invite_metadata(payload)
        )

    def serialize_poll(self, poll: Poll) -> Dict:
        return {
            "question": {"text": poll.question},
            "answers": self.serialize_poll_answers(poll.answers),
            "expiry": poll.expiry,
            "allow_multiselect": poll.allow_multiselect,
            "layout_type": poll.layout_type.value
        }

    @staticmethod
    def serialize_poll_answers(answers: List[PollAnswer]) -> List[Dict]:
        done_answers = []

        for answer in answers:
            done = {"answer_id": answer.answer_id}
            poll_media = {"text": answer.poll_media.text}

            if answer.poll_media.emoji is not None:
                emoji = answer.poll_media.emoji
                if emoji.id:
                    poll_media["emoji"] = attrs.asdict(answer.poll_media.emoji)
                else:
                    poll_media["emoji"] = {"id": None, "name": answer.poll_media.emoji.name}

            done["poll_media"] = poll_media
            done_answers.append(done)

        return done_answers

    @staticmethod
    def _deserialize_invite_metadata(payload: Dict) -> _InviteMetadata | None:
        if payload is None:
            return

        return _InviteMetadata(
            uses=payload.get("uses", 0),
            max_uses=payload.get("max_uses", 0),
            max_age=payload.get("max_age", 0),
            temporary=payload.get("temporary", False),
            created_at=iso_to_datetime(payload.get("created_at"))
        )

    @staticmethod
    def _deserialize_thread_metadata(payload: Dict) -> ThreadMetadata:
        return ThreadMetadata(
            archived=payload.get("archived", False),
            auto_archive_duration=payload.get("auto_archive_duration", 0),
            archive_timestamp=iso_to_datetime(payload.get("archive_timestamp")),
            locked=payload.get("locked", False),
            invitable=payload.get("invitable", False),
            create_timestamp=iso_to_datetime(payload.get("create_timestamp"))
        )

    def _deserialize_interaction_data(self, payload: Dict | None) -> InteractionData | None:
        if payload is None:
            return

        if (options := payload.get("options")) is not None:
            options = [self._deserialize_interaction_data_option(option) for option in options]

        if (components := payload.get("components")) is not None:
            components = [self._deserialize_component(component) for component in components]

        return InteractionData(
            id=Snowflake(payload.get("id", 0)),
            component_type=ComponentType(payload.get("component_type", 0)),
            type=payload.get("type"),
            custom_id=payload.get("custom_id"),
            name=payload.get("name"),
            option_type=payload.get("option_type"),
            guild_id=Snowflake(payload.get("guild_id", 0)),
            value=payload.get("value"),
            options=options,
            focused=payload.get("focused"),
            components=components,
            resolved=payload.get("resolved")
        )

    def _deserialize_component(self, payload: Dict | List) -> Any:
        from quant.entities.action_row import ActionRow

        component_type = payload.get("type")

        if component_type == ActionRow.INTERACTION_TYPE:
            return self.deserialize_action_row([component for component in payload.get("components")])

        if component_type == TextInput.INTERACTION_TYPE:
            return self.deserialize_text_input(payload)

        return payload

    def _deserialize_interaction_data_option(self, payload: Dict) -> InteractionDataOption:
        if (options := payload.get("options")) is not None:
            options = [self._deserialize_interaction_data_option(option) for option in options]

        return InteractionDataOption(
            name=payload.get("name"),
            value=payload.get("value"),
            type=SlashOptionType(payload.get("type", 0)),
            focused=payload.get("focused"),
            options=options
        )

    def _deserialize_reaction(self, payload: Dict) -> Reaction:
        if (guild_id := payload.get("guild_id")) is not None:
            guild_id = Snowflake(guild_id)

        if (member := payload.get("member")) is not None:
            member = self.deserialize_member(member, guild_id=guild_id)

        return Reaction(
            user_id=Snowflake(payload.get("user_id", 0)),
            type=payload.get("type"),
            message_id=Snowflake(payload.get("message_id", 0)),
            message_author_id=Snowflake(payload.get("message_author_id", 0)),
            member=member,
            emoji=payload.get("emoji"),
            channel_id=Snowflake(payload.get("channel_id", 0)),
            burst=payload.get("color"),
            guild_id=guild_id,
            burst_colors=payload.get("burst_colors")
        )
