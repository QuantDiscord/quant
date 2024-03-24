from __future__ import annotations

import asyncio
from io import BytesIO
import datetime
import json
import re
import warnings
from urllib.parse import urlencode
from typing import List, Any, Dict, Tuple, Final, TYPE_CHECKING, TypeVar

import aiohttp
import attrs

if TYPE_CHECKING:
    from quant.impl.core.commands import ApplicationCommandObject
    from quant.entities.action_row import ActionRow

from quant.impl.core.route import (
    Gateway as GatewayRoute,
    Message as MessageRoute,
    WebHook as WebhookRoute,
    Guild as GuildRoute,
    Interaction as InteractionRoute,
    Channel as ChannelRoute,
    User as UserRoute
)
from quant.impl.files import AttachableURL, File, file_to_bytes
from quant.entities.gateway import GatewayInfo, SessionStartLimitObject
from quant.impl.core.route import Route
from quant.entities.factory.entity_factory import EntityFactory
from quant.entities.message import MessageReference
from quant.entities.interactions.slash_option import ApplicationCommandOption
from quant.api.core.rest_aware import RESTAware
from quant.entities.snowflake import Snowflake
from quant.entities.member import GuildMember
from quant.entities.guild import Guild
from quant.entities.user import User
from quant.entities.roles import GuildRole
from quant.entities.emoji import Emoji
from quant.entities.invite import Invite
from quant.entities.modal.modal import ModalInteractionCallbackData
from quant.entities.interactions.interaction import InteractionCallbackData, InteractionCallbackType
from quant.entities.allowed_mentions import AllowedMentions
from quant.impl.core.http_manager import HttpManagerImpl, AcceptContentType
from quant.entities.message import Message, Attachment
from quant.entities.embeds import Embed
from quant.entities.webhook import Webhook
from quant.utils.cache.cache_manager import CacheManager

X_AUDIT_LOG_REASON: Final[str] = "X-Audit-Log-Reason"

SnowflakeT = TypeVar("SnowflakeT", bound=int | Snowflake)


class RESTImpl(RESTAware):
    def __init__(self, token: str, cache: CacheManager) -> None:
        self.http = HttpManagerImpl(authorization=token)
        self.token = token
        self.entity_factory = EntityFactory(cache)

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
        files: List[Any] = None,
        payload_json: str = None,
        attachments: List[Attachment] | None = None,
        flags: int = None,
        thread_name: str = None
    ) -> None:
        headers = {"Authorization": self.token}
        payload, form_data = await self._build_payload(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            files=files,
            payload_json=payload_json,
            attachments=attachments,
            flags=flags
        )
        payload["thread_name"] = thread_name

        await self.http.request(
            WebhookRoute.CREATE_WEBHOOK.method,
            webhook_url,
            form_data=form_data,
            headers=headers,
            pre_build_headers=False
        )

    async def create_webhook(self, channel_id: int, name: str, avatar: str = None, reason: str = None) -> Webhook:
        headers = {}
        method, url = self._build_url(
            route=WebhookRoute.CREATE_WEBHOOK,
            data={"channel_id": channel_id}
        )

        if reason is not None:
            headers[X_AUDIT_LOG_REASON] = reason

        payload = {"name": name, "avatar": avatar}
        webhook_data = await self.http.request(
            method=method, url=url, headers=headers, data=payload
        )
        return Webhook(**await webhook_data.json())

    async def fetch_emoji(self, guild_id: int, emoji: str) -> Emoji:
        if re.match(r"<:(\w+):(\w+)>", emoji):
            emoji_name, emoji_id = emoji.replace(">", "").replace("<", "").split(":")[1:]
            url = MessageRoute.GET_GUILD_EMOJI.uri.url_string.format(guild_id=guild_id, emoji_id=emoji_id)
            response = await self.http.request(
                MessageRoute.GET_GUILD_EMOJI.method,
                url=url,
                headers={"Content-Type": AcceptContentType.APPLICATION_X_WWW_FORM_URLENCODED}
            )

            return self.entity_factory.deserialize_emoji(await response.json())

        return self.entity_factory.deserialize_emoji({"name": emoji, "id": Snowflake(0)})

    async def create_reaction(
        self,
        emoji: str,
        guild_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        reason: str = None
    ) -> Emoji | str:
        headers = {}
        emoji = await self.fetch_emoji(guild_id=guild_id, emoji=emoji)

        if reason is not None:
            headers.update({X_AUDIT_LOG_REASON: reason})

        headers["Content-Type"] = AcceptContentType.APPLICATION_X_WWW_FORM_URLENCODED
        await self.http.request(
            MessageRoute.CREATE_REACTION.method,
            url=MessageRoute.CREATE_REACTION.uri.url_string.format(
                channel_id=channel_id,
                message_id=message_id,
                emoji=self._parse_emoji(emoji)
            ),
            headers=headers
        )

        return emoji

    async def delete_message(self, channel_id: int, message_id: int, reason: str = None) -> None:
        headers = {}
        method, url = self._build_url(
            route=MessageRoute.DELETE_MESSAGE,
            data={
                "channel_id": channel_id,
                "message_id": message_id
            }
        )

        if reason is not None:
            headers.update({X_AUDIT_LOG_REASON: reason})

        await self.http.request(
            method=method,
            url=url,
            headers=headers
        )

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
        files: List[Any] | None = None,
        payload_json: str | None = None,
        attachments: List[Attachment] | None = None,
        flags: int | None = None
    ) -> Message:
        payload, form_data = await self._build_payload(
            content=content,
            nonce=nonce,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=components,
            sticker_ids=sticker_ids,
            files=files,
            payload_json=payload_json,
            attachments=attachments,
            flags=flags
        )

        method, url = self._build_url(
            route=MessageRoute.CREATE_MESSAGE,
            data={"channel_id": channel_id}
        )
        response = await self.http.request(
            method=method,
            url=url,
            form_data=form_data,
            headers={"Authorization": self.token},
            pre_build_headers=False
        )
        message_json = await response.json()
        return self.entity_factory.deserialize_message(message_json)

    async def fetch_guild(self, guild_id: int, with_counts: bool = False) -> Guild:
        url_with_guild_id = GuildRoute.GET_GUILD.uri.url_string.format(guild_id=guild_id)
        build_guild_url = (
            url_with_guild_id
            if not with_counts
            else url_with_guild_id + "?with_counts=true"
        )
        data = await self.http.request(
            GuildRoute.GET_GUILD.method, build_guild_url
        )
        guild_data = await data.json()
        return self.entity_factory.deserialize_guild(guild_data)

    async def delete_guild(self, guild_id: int) -> None:
        method, url = self._build_url(
            route=GuildRoute.DELETE_GUILD,
            data={"guild_id": guild_id}
        )
        await self.http.request(method=method, url=url)

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
        method, url = self._build_url(route=GuildRoute.CREATE_GUILD)
        body = {'name': name, 'system_channel_flags': system_channel_flags}

        if region is not None:
            body["region"] = region

        if icon is not None:
            body["icon"] = icon

        if verification_level is not None:
            body["verification_level"] = verification_level

        if default_message_notifications is not None:
            body["default_message_notifications"] = default_message_notifications

        if explicit_content_filter is not None:
            body["explicit_content_filter"] = explicit_content_filter

        if roles is not None:
            body["roles"] = roles

        if channels is not None:
            body["channels"] = channels

        if afk_channel_id is not None:
            body["afl_channel_id"] = afk_channel_id

        if afk_timeout is not None:
            body["afk_timeout"] = afk_timeout

        if system_channel_id is not None:
            body["system_channel_id"] = system_channel_id

        data = await self.http.request(
            method=method, url=url, data=body
        )
        return self.entity_factory.deserialize_guild(await data.json())

    async def create_guild_ban(
        self,
        guild_id: SnowflakeT,
        member_id: SnowflakeT,
        reason: str,
        delete_message_days: int,
        delete_message_seconds: int
    ) -> None:
        payload = {
            'delete_message_days': delete_message_days,
            'delete_message_seconds': delete_message_seconds
        }
        headers = {}
        method, url = self._build_url(
            route=GuildRoute.CREATE_GUILD_BAN,
            data={
                "guild_id": guild_id,
                "user_id": member_id
            }
        )

        if delete_message_days > 0:
            warnings.warn("Option \"delete_message_days\" deprecated in Discord API", category=DeprecationWarning)

        if reason is not None:
            headers[X_AUDIT_LOG_REASON] = reason

        await self.http.request(
            method=method,
            url=url,
            # why linter warning here?
            headers=headers,  # type: ignore
            data=payload
        )

    async def remove_guild_member(
        self,
        user_id: SnowflakeT,
        guild_id: SnowflakeT,
        reason: str | None = None
    ) -> None:
        method, url = self._build_url(
            route=GuildRoute.REMOVE_GUILD_MEMBER,
            data={"user_id": user_id, "guild_id": guild_id}
        )
        headers = {}

        if reason is not None:
            headers[X_AUDIT_LOG_REASON] = reason

        await self.http.request(method=method, url=url, headers=headers)

    async def create_interaction_response(
        self,
        interaction_type: InteractionCallbackType,
        interaction_data: InteractionCallbackData | None,
        interaction_id: int,
        interaction_token: str
    ) -> None:
        interaction_payload = {"type": interaction_type.value}

        if interaction_data is not None:
            if isinstance(interaction_data, ModalInteractionCallbackData):
                interaction_payload["data"] = self.entity_factory.serialize_modal_interaction_callback_data(interaction_data)
            else:
                interaction_payload["data"] = self.entity_factory.serialize_interaction_callback_data(interaction_data)

        payload, form_data = await self._build_payload(
            **attrs.asdict(interaction_data),
            payload_json=interaction_payload
        )
        method, url = self._build_url(
            route=InteractionRoute.CREATE_INTERACTION_RESPONSE,
            data={"interaction_id": interaction_id, "interaction_token": interaction_token}
        )

        await self.http.request(
            method=method,
            url=url,
            form_data=form_data,
            pre_build_headers=False,
            headers={"Authorization": self.token}
        )

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
        files: List[Any] = None,
        payload_json: str = None,
        attachments: List[Attachment] | None = None,
        flags: int = None,
        thread_name: str = None
    ) -> None:
        method, url = self._build_url(
            route=WebhookRoute.CREATE_FOLLOWUP_MESSAGE,
            data={"application_id": application_id, "interaction_token": interaction_token},
            query_params={"wait": True}
        )
        payload, _ = await self._build_payload(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            files=files,
            payload_json=payload_json,
            attachments=attachments,
            flags=flags
        )

        if thread_name is not None:
            payload["thread_name"] = thread_name

        await self.http.request(method=method, url=url, data=payload)

    async def fetch_message(self, channel_id: int, message_id: int) -> Message:
        method, url = self._build_url(
            route=MessageRoute.GET_MESSAGE,
            data={"channel_id": channel_id, "message_id": message_id}
        )
        raw_message = await self.http.request(method=method, url=url)

        return self.entity_factory.deserialize_message(await raw_message.json())

    async def create_application_command(
        self,
        application_id: int,
        name: str,
        description: str,
        default_permissions: bool = False,
        dm_permissions: bool = False,
        default_member_permissions: str = None,
        options: List[ApplicationCommandOption] = None,
        nsfw: bool = False
    ) -> ApplicationCommandObject:
        body = {"name": name, "description": description}
        method, url = self._build_url(
            route=InteractionRoute.CREATE_APPLICATION_COMMAND,
            data={"application_id": application_id}
        )

        if default_permissions:
            body["default_permissions"] = default_permissions

        if dm_permissions:
            body["dm_permissions"] = dm_permissions

        if default_member_permissions is not None:
            body["default_member_permissions"] = default_member_permissions

        if options is not None:
            body["options"] = [self.entity_factory.serialize_slash_option(option) for option in options]

        if nsfw:
            body["nsfw"] = nsfw

        response = await self.http.request(
            method=method,
            url=url,
            data=body
        )

        return self.entity_factory.deserialize_application_command(await response.json())

    async def create_guild_application_command(
        self,
        application_id: int,
        name: str,
        description: str,
        guild_id: SnowflakeT,
        default_permissions: bool = False,
        dm_permissions: bool = False,
        default_member_permissions: str = None,
        options: List[ApplicationCommandOption] = None,
        nsfw: bool = False
    ) -> ApplicationCommandObject:
        body = {"name": name, "description": description}
        method, url = self._build_url(
            route=InteractionRoute.CREATE_GUILD_APPLICATION_COMMAND,
            data={"application_id": application_id, "guild_id": guild_id}
        )

        if default_permissions:
            body["default_permissions"] = default_permissions

        if dm_permissions:
            body["dm_permissions"] = dm_permissions

        if default_member_permissions is not None:
            body["default_member_permissions"] = default_member_permissions

        if guild_id is not None:
            body["guild_id"] = guild_id

        if options is not None:
            body["options"] = [self.entity_factory.serialize_slash_option(option) for option in options]

        if nsfw:
            body["nsfw"] = nsfw

        response = await self.http.request(
            method=method,
            url=url,
            data=body
        )

        return self.entity_factory.deserialize_application_command(await response.json())

    async def delete_guild_application_command(
        self,
        application_id: int,
        guild_id: SnowflakeT,
        command_id: SnowflakeT
    ) -> None:
        method, url = self._build_url(
            route=InteractionRoute.DELETE_GUILD_APPLICATION_COMMAND,
            data={
                "application_id": application_id,
                "guild_id": guild_id,
                "command_id": command_id
            }
        )
        await self.http.request(method=method, url=url)

    async def fetch_guild_application_commands(
        self,
        application_id: int,
        guild_id: int,
        with_localizations: bool = False
    ) -> List[ApplicationCommandObject]:
        method, url = self._build_url(
            route=InteractionRoute.GET_GUILD_APPLICATION_COMMANDS,
            data={
                "application_id": application_id,
                "guild_id": guild_id
            },
            query_params={
                "with_localizations": with_localizations
            }
        )
        response = await self.http.request(method=method, url=url)

        return [self.entity_factory.deserialize_application_command(command) for command in await response.json()]

    async def fetch_initial_interaction_response(self, application_id: int, interaction_token: str) -> Message:
        method, url = self._build_url(
            route=InteractionRoute.GET_ORIGINAL_INTERACTION_RESPONSE,
            data={"application_id": application_id, "interaction_token": interaction_token}
        )
        response = await self.http.request(
            method=method,
            url=url
        )

        return self.entity_factory.deserialize_message(await response.json())

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
        payload, _ = await self._build_payload(
            content=content,
            embeds=embeds,
            embed=embed,
            flags=flags,
            allowed_mentions=allowed_mentions,
            components=components
        )
        method, url = self._build_url(
            route=MessageRoute.EDIT_MESSAGE,
            data={"channel_id": channel_id, "message_id": message_id}
        )
        response = await self.http.request(
            method=method,
            url=url,
            data=payload
        )

        return self.entity_factory.deserialize_message(await response.json())

    async def delete_all_reactions(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        method, url = self._build_url(
            route=MessageRoute.DELETE_ALL_REACTIONS,
            data={"channel_id": channel_id, "message_id": message_id}
        )
        await self.http.request(method=method, url=url)

    async def delete_all_reactions_for_emoji(
        self,
        guild_id: SnowflakeT,
        channel_id: SnowflakeT,
        message_id: SnowflakeT,
        emoji: str | Snowflake | Emoji
    ) -> None:
        parsed_emoji = self._parse_emoji(await self.fetch_emoji(guild_id=guild_id, emoji=emoji))
        method, url = self._build_url(
            route=MessageRoute.DELETE_ALL_REACTION_FOR_EMOJI,
            data={"channel_id": channel_id, "message_id": message_id, "emoji": parsed_emoji}
        )
        await self.http.request(
            method=method,
            url=url,
            headers={"Content-Type": AcceptContentType.APPLICATION_X_WWW_FORM_URLENCODED}
        )

    async def edit_original_interaction_response(
        self,
        application_id: SnowflakeT,
        interaction_token: str,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: ActionRow | None = None,
        files: List[Any] | None = None,
        payload_json: str | None = None,
        attachments: List[Attachment] | None = None,
        thread_id: SnowflakeT = None
    ) -> Message:
        method, url = self._build_url(
            route=InteractionRoute.EDIT_ORIGINAL_INTERACTION_RESPONSE,
            data={"application_id": application_id, "interaction_token": interaction_token}
        )

        payload, _ = await self._build_payload(
            content=content,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            files=files,
            payload_json=payload_json,
            attachments=attachments
        )

        if thread_id is not None:
            url += f"?thread_id={thread_id}"

        response = await self.http.request(
            method=method, url=url, data=payload
        )
        return self.entity_factory.deserialize_message(await response.json())

    async def fetch_invite(
        self,
        invite_code: str,
        with_counts: bool = False,
        with_expiration: bool = False,
        guild_scheduled_event_id: Snowflake | None = None
    ) -> Invite:
        method, url = self._build_url(
            route=GuildRoute.GET_INVITE,
            data={"invite_code": invite_code},
            query_params={
                "with_counts": with_counts,
                "with_expiration": with_expiration,
                "guild_scheduled_event_id": guild_scheduled_event_id
            }
        )
        response = await self.http.request(method=method, url=url)

        return Invite(**await response.json())

    async def delete_invite(self, invite_code: str, reason: str | None = None) -> Invite:
        method, url = self._build_url(
            route=GuildRoute.DELETE_INVITE,
            data={"invite_code": invite_code}
        )
        headers = {}

        if reason is not None:
            headers[X_AUDIT_LOG_REASON] = reason

        response = await self.http.request(
            method=method, url=url, headers=headers
        )

        return Invite(**await response.json())

    async def fetch_guild_invites(self, guild_id: Snowflake) -> List[Invite]:
        method, url = self._build_url(
            route=GuildRoute.GET_GUILD_INVITES,
            data={"guild_id": guild_id}
        )
        response = await self.http.request(
            method=method, url=url
        )
        return [self.entity_factory.deserialize_invite(invite) for invite in await response.json()]

    async def fetch_guild_members(
        self,
        guild_id: SnowflakeT,
        limit: int = 1,
        after: Snowflake = Snowflake(0)
    ) -> List[GuildMember]:
        method, url = self._build_url(
            route=GuildRoute.GET_GUILD_MEMBERS,
            data={"guild_id": guild_id},
            query_params={"limit": limit, "after": after}
        )
        response = await self.http.request(method=method, url=url)
        return [self.entity_factory.deserialize_member(member, guild_id=guild_id) for member in await response.json()]

    async def fetch_guild_roles(self, guild_id: SnowflakeT) -> List[GuildRole]:
        method, url = self._build_url(
            route=GuildRoute.GET_GUILD_ROLES,
            data={"guild_id": guild_id}
        )
        response = await self.http.request(method=method, url=url)
        return [self.entity_factory.deserialize_role(role) for role in await response.json()]

    async def fetch_user(self, user_id: SnowflakeT) -> User:
        method, url = self._build_url(
            route=UserRoute.GET_USER,
            data={"user_id": user_id}
        )
        response = await self.http.request(method=method, url=url)
        return self.entity_factory.deserialize_user(await response.json())

    async def fetch_guild_member(self, guild_id: SnowflakeT, user_id: SnowflakeT) -> GuildMember:
        method, url = self._build_url(
            route=GuildRoute.GET_GUILD_MEMBER,
            data={"guild_id": guild_id, "user_id": user_id}
        )
        response = await self.http.request(method=method, url=url)
        return self.entity_factory.deserialize_member(await response.json(), guild_id=guild_id)

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
        headers = {}
        payload = {}
        method, url = self._build_url(
            route=GuildRoute.MODIFY_GUILD_MEMBER,
            data={"user_id": user_id, "guild_id": guild_id}
        )

        if nick is not None:
            payload["nick"] = nick

        if roles is not None:
            payload["roles"] = roles

        if move_channel_id is not None:
            payload["mute"] = mute
            payload["deaf"] = deaf
            payload["channel_id"] = move_channel_id

        if communication_disabled_until is not None:
            payload["communication_disabled_until"] = communication_disabled_until

        if flags is not None:
            payload["flags"] = flags

        if reason is not None:
            headers[X_AUDIT_LOG_REASON] = reason

        response = await self.http.request(method=method, url=url, data=payload)
        return self.entity_factory.deserialize_member(await response.json(), guild_id=guild_id)

    async def add_guild_member_role(
        self,
        guild_id: SnowflakeT,
        user_id: SnowflakeT,
        role_id: SnowflakeT
    ) -> None:
        method, url = self._build_url(
            route=GuildRoute.ADD_GUILD_MEMBER_ROLE,
            data={"guild_id": guild_id, "user_id": user_id, "role_id": role_id}
        )

        await self.http.request(method=method, url=url)

    async def get_gateway(self) -> GatewayInfo:
        method, url = self._build_url(route=GatewayRoute.GATEWAY_BOT)
        response = await self.http.request(method=method, url=url)
        payload = await response.json()

        return GatewayInfo(
            url=payload.get("url"),
            shards=payload.get("shards"),
            session_start_limit=SessionStartLimitObject(**payload.get("session_start_limit"))
        )

    @staticmethod
    def _parse_emoji(emoji: str | Emoji | SnowflakeT) -> str:
        return str(emoji).replace("<", "").replace(">", "") if emoji.id > 0 else emoji

    @staticmethod
    def _build_url(
        route: Route,
        data: Dict[str, Any] = None,
        query_params: Dict[str, Any] = None
    ) -> Tuple[str, str]:
        url = route.uri.url_string
        if data is not None:
            url = route.uri.url_string.format(**data)

        if query_params is not None:
            if '?' in url:
                separator = '&'
            else:
                separator = '?'

            query_string = urlencode(query_params)
            url += f"{separator}{query_string}"

        return route.method, url

    async def _build_payload(
        self,
        content: str | None = None,
        nonce: str | int | None = None,
        tts: bool = False,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        message_reference: MessageReference | None = None,
        components: ActionRow | None = None,
        sticker_ids: List | None = None,
        files: Any | None = None,
        payload_json: Any | None = None,
        attachments: List[Attachment] | None = None,
        flags: int | None = None
    ) -> Tuple[Dict, aiohttp.FormData]:
        body = {}
        form_data = aiohttp.FormData()

        if content is not None:
            body["content"] = content

        if nonce is not None:
            body["nonce"] = nonce

        if tts is not None:
            body["tts"] = tts

        if embed is not None:
            body["embeds"] = [self.entity_factory.serialize_embed(embed)]

        if embeds is not None:
            body["embeds"] = [self.entity_factory.serialize_embed(e) for e in embeds]

        if allowed_mentions is not None:
            body["allowed_mentions"] = attrs.asdict(allowed_mentions)

        if message_reference is not None:
            body["message_reference"] = attrs.asdict(message_reference)

        if components is not None:
            body["components"] = [self.entity_factory.serialize_action_row(components)]

        if sticker_ids is not None:
            body["sticker_ids"] = sticker_ids

        if files is not None:
            body["files"] = files

        if attachments is not None:
            body["attachments"] = [self.entity_factory.serialize_attachment(i, attach) for i, attach in enumerate(attachments)]

            for attachment_id, attachment in enumerate(attachments):
                if isinstance(attachment, AttachableURL | Attachment):
                    attachment_data = await self.http.request(
                        method="GET",
                        url=attachment.url,
                        pre_build_headers=False
                    )
                    content = attachment_data.content
                    buffer = b""

                    async for chunk, _ in content.iter_chunks():
                        buffer += chunk

                    attachment = buffer
                elif isinstance(attachment, File):
                    attachment = file_to_bytes(attachment)
                else:
                    raise ValueError("Unsupported attachment type")

                filename = f"files[{attachment_id}]"
                form_data.add_field(
                    filename,
                    attachment,
                    filename=filename
                )

        if flags is not None:
            body["flags"] = flags

        if payload_json is not None:
            form_data.add_field("payload_json", json.dumps(payload_json))
        else:
            form_data.add_field("payload_json", json.dumps(body))

        return body, form_data
