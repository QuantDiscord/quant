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
from abc import ABC, abstractmethod
from typing import List, Any, Dict, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from quant.impl.core.commands import ApplicationCommandObject, ApplicationCommandContexts
    from quant.entities.action_row import ActionRow

from quant.impl.files import AttachableURL, File
from quant.entities.gateway import GatewayInfo
from quant.entities.interactions.application_command import ApplicationCommandTypes
from quant.entities.message import MessageReference
from quant.entities.interactions.slash_option import ApplicationCommandOption
from quant.entities.snowflake import Snowflake
from quant.entities.member import GuildMember
from quant.entities.guild import Guild
from quant.entities.user import User
from quant.entities.roles import GuildRole
from quant.entities.emoji import Emoji
from quant.entities.invite import Invite
from quant.entities.integration import IntegrationTypes
from quant.entities.modal.modal import ModalInteractionCallbackData
from quant.entities.interactions.interaction import InteractionCallbackData, InteractionCallbackType
from quant.entities.allowed_mentions import AllowedMentions
from quant.entities.message import Message, Attachment
from quant.entities.embeds import Embed
from quant.entities.webhook import Webhook
from quant.entities.poll import Poll
from quant.entities.locales import DiscordLocale

SnowflakeT = TypeVar("SnowflakeT", bound=int | Snowflake)
AttachmentT = TypeVar("AttachmentT", bound=AttachableURL | File | Attachment)


class RESTAware(ABC):
    @abstractmethod
    async def execute_webhook(
        self,
        webhook_url: str,
        content: str = None,
        username: str = None,
        avatar_url: str = None,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        components: List[Any] = None,
        payload_json: str = None,
        attachments: List[AttachmentT] | None = None,
        flags: int = None,
        thread_name: str = None
    ) -> None:
        """
        Executes a webhook.

        Parameters
        ==========
        webhook_url: :class:`str`

        content: :class:`str`

        username: :class:`str`

        avatar_url: :class:`str`

        tts: :class:`bool`

        embed: :class:`Embed`

        embeds: List[:class:`Embed`]

        allowed_mentions: :class:`AllowedMentions`

        components: List[:class:`Any`]

        payload_json: :class:`str`

        attachments: List[:class:`AttachmentT`] | None

        flags: :class:`int`

        thread_name: :class:`str`
        """

    @abstractmethod
    async def create_webhook(self, channel_id: int, name: str, avatar: str = None, reason: str = None) -> Webhook:
        """
        Creates a webhook.


        Parameters
        ==========
        channel_id: :class:`int`

        name: :class:`str`

        avatar: :class:`str`

        reason: :class:`str`
        """

    @abstractmethod
    async def fetch_emoji(self, guild_id: int, emoji: str) -> Emoji:
        """
        Fetches an emoji.

        Parameters
        ==========
        guild_id: :class:`int`

        emoji: :class:`str`
        """

    @abstractmethod
    async def create_reaction(
        self,
        emoji: str,
        guild_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        reason: str = None
    ) -> Emoji | str:
        """
        Creates a reaction.

        Parameters
        ==========
        emoji: :class:`str`

        guild_id: :class:`int`

        channel_id: :class:`int`

        message_id: :class:`int`

        reason: :class:`str`
        """

    @abstractmethod
    async def delete_message(self, channel_id: int, message_id: int, reason: str = None) -> None:
        """
        Deletes a message.

        Parameters
        ==========
        channel_id: :class:`int`

        message_id: :class:`int`

        reason: :class:`str`
        """

    @abstractmethod
    async def create_message(
        self,
        channel_id: int,
        content: str | None = None,
        nonce: str | int | None = None,
        tts: bool = False,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        message_reference: MessageReference = None,
        components: ActionRow | None = None,
        sticker_ids: List = None,
        payload_json: str | None = None,
        attachments: List[AttachmentT] | None = None,
        flags: int | None = None,
        poll: Poll | None = None
    ) -> Message:
        """
        Creates a message.

        Parameters
        ==========
        channel_id: :class:`int`

        content: :class:`str`

        nonce: :class:`str` | :class:`int`

        tts: :class:`bool`

        embed: :class:`Embed`

        embeds: List[:class:`Embed`] | None

        allowed_mentions: :class:`AllowedMentions` | None

        message_reference: :class:`MessageReference`

        components: :class:`ActionRow` | None

        sticker_ids: :class:`List`

        payload_json: :class:`str` | None

        attachments: List[:class:`AttachmentT`] | None

        flags: :class:`int` | None

        poll: :class:`Poll` | None
        """

    @abstractmethod
    async def fetch_guild(self, guild_id: int, with_counts: bool = False) -> Guild:
        """
        Fetches a guild.

        Parameters
        ==========
        guild_id: :class:`int`

        with_counts: :class:`bool`
        """

    @abstractmethod
    async def delete_guild(self, guild_id: int) -> None:
        """
        Deletes a guild.

        Parameters
        ==========
        guild_id: :class:`int`
        """

    @abstractmethod
    async def create_guild(
        self,
        name: str,
        region: str = None,
        icon: Any = None,
        verification_level: int | None = None,
        default_message_notifications: int | None = None,
        explicit_content_filter: int | None = None,
        roles: List[Any] = None,
        channels: List[Any] = None,
        afk_channel_id: int | None = None,
        afk_timeout: int | None = None,
        system_channel_id: int | None = None,
        system_channel_flags: int = 0
    ) -> Guild:
        """
        Creates a guild.

        Parameters
        ==========
        name: :class:`str`

        region: :class:`str`

        icon: :class:`Any`

        verification_level: :class:`int` | None

        default_message_notifications: :class:`int` | None

        explicit_content_filter: :class:`int` | None

        roles: :class:`List`

        channels: :class:`List`

        afk_channel_id: :class:`int` | None

        afk_timeout: :class:`int` | None

        system_channel_id: :class:`int` | None

        system_channel_flags: :class:`int`
        """

    @abstractmethod
    async def create_guild_ban(
        self,
        guild_id: SnowflakeT,
        member_id: SnowflakeT,
        reason: str,
        delete_message_days: int,
        delete_message_seconds: int
    ) -> None:
        """
        Bans a member from a guild.

        Parameters
        ==========
        guild_id: :class:`SnowflakeT`

        member_id: :class:`SnowflakeT`

        reason: :class:`str`

        delete_message_days: :class:`int`

        delete_message_seconds: :class:`int`
        """

    @abstractmethod
    async def remove_guild_member(
        self,
        user_id: SnowflakeT,
        guild_id: SnowflakeT,
        reason: str | None = None
    ) -> None:
        """
        Removes a member from a guild.

        Parameters
        ==========
        user_id: :class:`SnowflakeT`

        guild_id: :class:`SnowflakeT`

        reason: :class:`str | None`
        """

    @abstractmethod
    async def create_interaction_response(
        self,
        interaction_type: InteractionCallbackType,
        interaction_data: InteractionCallbackData | ModalInteractionCallbackData | None,
        interaction_id: int,
        interaction_token: str
    ) -> None:
        """
        Creates an interaction response.

        Parameters
        ==========
        interaction_type: :class:`InteractionCallbackType`

        interaction_data: :class:`InteractionCallbackData | ModalInteractionCallbackData | None`

        interaction_id: :class:`int`

        interaction_token: :class:`str`
        """

    @abstractmethod
    async def create_followup_message(
        self,
        application_id: int,
        interaction_token: str,
        content: str = None,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        components: List[Any] = None,
        payload_json: str = None,
        attachments: List[AttachmentT] | None = None,
        flags: int = None,
        thread_name: str = None
    ) -> None:
        """
        Creates a follow-up message for an interaction.

        Parameters
        ==========
        application_id: :class:`int`

        interaction_token: :class:`str`

        content: :class:`str`

        tts: :class:`bool`

        embed: :class:`Embed`

        embeds: :class:`List[Embed]`

        allowed_mentions: :class:`AllowedMentions`

        components: :class:`List[Any]`

        payload_json: :class:`str`

        attachments: List[:class:`AttachmentT`] | None

        flags: :class:`int`

        thread_name: :class:`str`
        """

    @abstractmethod
    async def fetch_message(self, channel_id: int, message_id: int) -> Message:
        """
        Fetches a message.

        Parameters
        ==========
        channel_id: :class:`int`

        message_id: :class:`int`
        """

    @abstractmethod
    async def create_application_command(
        self,
        application_id: int,
        name: str,
        description: str,
        name_localizations: Dict[DiscordLocale, str] | None = None,
        description_localizations: Dict[DiscordLocale, str] | None = None,
        app_cmd_type: ApplicationCommandTypes = ApplicationCommandTypes.CHAT_INPUT,
        default_permissions: bool = False,
        dm_permissions: bool = False,
        default_member_permissions: str = None,
        options: List[ApplicationCommandOption] = None,
        nsfw: bool = False,
        integration_types: List[IntegrationTypes] = None,
        contexts: List[ApplicationCommandContexts] = None
    ) -> ApplicationCommandObject:
        """
        Creates a global application command.

        Parameters
        ==========
        application_id: :class:`int`

        name: :class:`str`

        description: :class:`str`

        name_localizations: Dict[:class:`DiscordLocale`, :class:`str`] | None

        description_localizations: Dict[:class:`DiscordLocale`, :class:`str`] | None

        app_cmd_type: :class:`ApplicationCommandTypes`

        default_permissions: :class:`bool`

        dm_permissions: :class:`bool`

        default_member_permissions: :class:`str`

        options: List[:class:`ApplicationCommandOption`]

        nsfw: :class:`bool`

        integration_types: List[:class:`IntegrationTypes`]

        contexts: List[:class:`ApplicationCommandContexts`]
        """

    @abstractmethod
    async def create_guild_application_command(
        self,
        application_id: int,
        name: str,
        description: str,
        guild_id: SnowflakeT,
        name_localizations: Dict[DiscordLocale, str] | None = None,
        description_localizations: Dict[DiscordLocale, str] | None = None,
        app_cmd_type: ApplicationCommandTypes = ApplicationCommandTypes.CHAT_INPUT,
        default_permissions: bool = False,
        dm_permissions: bool = False,
        default_member_permissions: str = None,
        options: List[ApplicationCommandOption] = None,
        nsfw: bool = False,
        integration_types: List[IntegrationTypes] = None,
        contexts: List[ApplicationCommandContexts] = None
    ) -> ApplicationCommandObject:
        """
        Creates a guild application command.

        Parameters
        ==========
        application_id: :class:`int`

        name: :class:`str`

        description: :class:`str`

        guild_id: :class:`SnowflakeT`

        name_localizations: Dict[:class:`DiscordLocale`, :class:`str`] | None

        description_localizations: Dict[:class:`DiscordLocale`, :class:`str`] | None

        app_cmd_type: :class:`ApplicationCommandTypes`

        default_permissions: :class:`bool`

        dm_permissions: :class:`bool`

        default_member_permissions: :class:`str`

        options: :class:`List[ApplicationCommandOption]`

        nsfw: :class:`bool`

        integration_types: :class:`List[IntegrationTypes]`

        contexts: :class:`List[ApplicationCommandContexts]`
        """

    @abstractmethod
    async def delete_guild_application_command(
        self,
        application_id: int,
        guild_id: SnowflakeT,
        command_id: SnowflakeT
    ) -> None:
        """
        Deletes a guild application command.

        Parameters
        ==========
        application_id: :class:`int`

        guild_id: :class:`SnowflakeT`

        command_id: :class:`SnowflakeT`
        """

    @abstractmethod
    async def delete_global_application_command(
        self,
        application_id: int,
        command_id: SnowflakeT
    ) -> None:
        """
        Deletes a global application command.

        application_id: :class:`int`

        command_id: :class:`SnowflakeT`
        """

    @abstractmethod
    async def fetch_guild_application_commands(
        self,
        application_id: int,
        guild_id: int,
        with_localizations: bool = False
    ) -> List[ApplicationCommandObject]:
        """
        Fetches guild application commands.

        Parameters
        ==========
        application_id: :class:`int`

        guild_id: :class:`int`

        with_localizations: :class:`bool`
        """

    @abstractmethod
    async def fetch_global_application_commands(
        self,
        application_id: int,
        with_localizations: bool = False
    ) -> List[ApplicationCommandObject]:
        """
        Fetches global application commands.

        Parameters
        ==========
        application_id: :class:`int`

        with_localizations: :class:`bool`
        """

    @abstractmethod
    async def fetch_initial_interaction_response(self, application_id: int, interaction_token: str) -> Message:
        """
        Fetches the initial interaction response.

        Parameters
        ==========
        application_id: :class:`int`

        interaction_token: :class:`str`
        """

    @abstractmethod
    async def edit_message(
        self,
        channel_id: SnowflakeT,
        message_id: SnowflakeT,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        flags: int | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: ActionRow | None = None
    ) -> Message:
        """
        Edits a message.

        Parameters
        ==========
        channel_id: :class:`SnowflakeT`

        message_id: :class:`SnowflakeT`

        content: :class:`str`

        embed: :class:`Embed`

        embeds: :class:`List[Embed]` | None

        flags: :class:`int` | None

        allowed_mentions: :class:`AllowedMentions` | None

        components: :class:`ActionRow` | None
        """

    @abstractmethod
    async def delete_all_reactions(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        """
        Deletes all reactions from a message.

        Parameters
        ==========
        channel_id: :class:`Snowflake`

        message_id: :class:`Snowflake`
        """

    @abstractmethod
    async def delete_all_reactions_for_emoji(
        self,
        guild_id: SnowflakeT,
        channel_id: SnowflakeT,
        message_id: SnowflakeT,
        emoji: str | Snowflake | Emoji
    ) -> None:
        """
        Deletes all reactions for a specific emoji from a message.

        Parameters
        ==========
        guild_id: :class:`SnowflakeT`

        channel_id: :class:`SnowflakeT`

        message_id: :class:`SnowflakeT`

        emoji: :class:`str` | :class:`Snowflake` | :class:`Emoji`
        """

    @abstractmethod
    async def edit_original_interaction_response(
        self,
        application_id: SnowflakeT,
        interaction_token: str,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: ActionRow | None = None,
        payload_json: str | None = None,
        attachments: List[AttachmentT] | None = None,
        thread_id: SnowflakeT = None
    ) -> Message:
        """
        Edits the original interaction response.

        Parameters
        ==========
        application_id: :class:`SnowflakeT`

        interaction_token: :class:`str`

        content: :class:`str`

        embed: :class:`Embed`

        embeds: :class:`List[Embed]`

        allowed_mentions: :class:`AllowedMentions`

        components: :class:`ActionRow`

        payload_json: :class:`str`

        attachments: :class:`List[AttachmentT]`

        thread_id: :class:`SnowflakeT`
        """

    @abstractmethod
    async def bulk_overwrite_global_app_commands(
        self, application_id: SnowflakeT, commands: List[ApplicationCommandObject] | None = None
    ) -> List[ApplicationCommandObject]:
        """
        Bulk overwrites global application commands.

        Parameters
        ==========
        application_id: :class:`SnowflakeT`

        commands: List[:class:`ApplicationCommandObject`]
        """

    @abstractmethod
    async def bulk_overwrite_guild_app_commands(
        self,
        application_id: SnowflakeT,
        guild_id: SnowflakeT,
        commands: List[ApplicationCommandObject] | None = None
    ) -> List[ApplicationCommandObject]:
        """
        Bulk overwrites guild application commands.

        Parameters
        ==========
        application_id: :class:`SnowflakeT`

        guild_id: :class:`SnowflakeT`

        commands: List[:class:`ApplicationCommandObject`]
        """

    @abstractmethod
    async def fetch_invite(
        self,
        invite_code: str,
        with_counts: bool = False,
        with_expiration: bool = False,
        guild_scheduled_event_id: Snowflake | None = None
    ) -> Invite:
        """
        Fetches an invite.

        Parameters
        ==========
        invite_code: :class:`str`

        with_counts: :class:`bool`

        with_expiration: :class:`bool`

        guild_scheduled_event_id: :class:`Snowflake`
        """

    @abstractmethod
    async def delete_invite(self, invite_code: str, reason: str | None = None) -> Invite:
        """
        Deletes an invite.

        Parameters
        ==========
        invite_code: :class:`str`

        reason: :class:`str`
        """

    @abstractmethod
    async def fetch_guild_invites(self, guild_id: Snowflake) -> List[Invite]:
        """
        Fetches invites for a guild.

        Parameters
        ==========
        guild_id: :class:`Snowflake`
        """

    @abstractmethod
    async def fetch_guild_members(
        self,
        guild_id: SnowflakeT,
        limit: int = 1,
        after: Snowflake = Snowflake(0)
    ) -> List[GuildMember]:
        """
        Fetches guild members.

        Parameters
        ==========
        guild_id: :class:`SnowflakeT`

        limit: :class:`int`

        after: :class:`Snowflake`
        """

    @abstractmethod
    async def fetch_guild_roles(self, guild_id: SnowflakeT) -> List[GuildRole]:
        """
        Fetches guild roles.

        Parameters
        ==========
        guild_id: :class:`SnowflakeT`
        """

    @abstractmethod
    async def fetch_user(self, user_id: SnowflakeT) -> User:
        """
        Fetches a user.

        Parameters
        ==========
        user_id: :class:`SnowflakeT`
        """

    @abstractmethod
    async def fetch_guild_member(self, guild_id: SnowflakeT, user_id: SnowflakeT) -> GuildMember:
        """
        Fetches a guild member.

        Parameters
        ==========
        guild_id: :class:`SnowflakeT`

        user_id: :class:`SnowflakeT`
        """

    @abstractmethod
    async def modify_guild_member(
        self,
        user_id: SnowflakeT,
        guild_id: SnowflakeT,
        nick: str | None = None,
        roles: List[SnowflakeT] | None = None,
        mute: bool | None = None,
        deaf: bool | None = None,
        move_channel_id: SnowflakeT = None,
        communication_disabled_until: datetime.datetime | None = None,
        flags: int | None = None,
        reason: str | None = None
    ) -> GuildMember:
        """
        Modifies a guild member.

        Parameters
        ==========
        user_id: :class:`SnowflakeT`

        guild_id: :class:`SnowflakeT`

        nick: :class:`str`

        roles: :class:`List[SnowflakeT]`

        mute: :class:`bool`

        deaf: :class:`bool`

        move_channel_id: :class:`SnowflakeT`

        communication_disabled_until: :class:`datetime.datetime`

        flags: :class:`int`

        reason: :class:`str`
        """

    @abstractmethod
    async def add_guild_member_role(
        self,
        guild_id: SnowflakeT,
        user_id: SnowflakeT,
        role_id: SnowflakeT
    ) -> None:
        """
        Adds a role to a guild member.

        Parameters
        ==========
        guild_id: :class:`SnowflakeT`

        user_id: :class:`SnowflakeT`

        role_id: :class:`SnowflakeT`
        """

    @abstractmethod
    async def get_gateway(self) -> GatewayInfo:
        """
        Gets the gateway information.
        """

    @abstractmethod
    async def get_poll_answers(
        self,
        channel_id: SnowflakeT,
        message_id: SnowflakeT,
        answer_id: int,
        after: Snowflake | None = Snowflake(0),
        limit: int = 100
    ) -> List[User]:
        """
        Gets poll answers.

        Parameters
        ==========
        channel_id: :class:`SnowflakeT`

        message_id: :class:`SnowflakeT`

        answer_id: :class:`int`

        after: :class:`Snowflake`

        limit: :class:`int`
        """

    @abstractmethod
    async def end_poll_immediately(self, channel_id: SnowflakeT, message_id: SnowflakeT) -> Message:
        """[coro]

        Ends poll

        Parameters
        ==========
        channel_id: :class:`SnowflakeT`

        message_id: :class:`SnowflakeT`
        """
