import re
import warnings
from typing import List, Any, Dict

import attrs

from quant.impl.core.route import Route
from quant.entities.action_row import ActionRow
from quant.entities.message import MessageReference
from quant.entities.interactions.slash_option import SlashOption
from quant.api.core.rest_aware import RESTAware
from quant.entities.snowflake import Snowflake
from quant.entities.guild import Guild
from quant.entities.emoji import Emoji
from quant.entities.invite import Invite
from quant.entities.interactions.interaction import InteractionCallbackData, InteractionCallbackType
from quant.entities.allowed_mentions import AllowedMentions
from quant.impl.core.http_manager import HttpManagerImpl
from quant.impl.core.route import (
    CREATE_MESSAGE, DELETE_MESSAGE,
    CREATE_WEBHOOK, GET_GUILD, CREATE_GUILD,
    DELETE_GUILD, CREATE_REACTION, GET_GUILD_EMOJI,
    CREATE_INTERACTION_RESPONSE, GET_MESSAGE, EDIT_MESSAGE,
    CREATE_APPLICATION_COMMAND, GET_ORIGINAL_INTERACTION_RESPONSE, EDIT_ORIGINAL_INTERACTION_RESPONSE,
    CREATE_GUILD_BAN, DELETE_ALL_REACTIONS, DELETE_ALL_REACTION_FOR_EMOJI, GET_INVITE, DELETE_INVITE,
    GET_GUILD_INVITES
)
from quant.entities.message import Message
from quant.entities.embeds import Embed
from quant.entities.webhook import Webhook
from quant.impl.json_object import MutableJsonBuilder


class DiscordREST(RESTAware):
    def __init__(self, token: str) -> None:
        self.http = HttpManagerImpl(authorization=token)
        self.token = token

    def _build_payload(
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
        attachments: List[Any] | None = None,
        flags: int | None = None
    ) -> MutableJsonBuilder:
        body = MutableJsonBuilder()

        if content is not None:
            body.put("content", content)

        if nonce is not None:
            body.put("nonce", nonce)

        if tts is not None:
            body.put("tts", tts)

        if embed is not None:
            body.put("embeds", [embed])

        if embeds is not None:
            body.put("embeds", embed)

        if allowed_mentions is not None:
            body.put("allowed_mentions", attrs.asdict(allowed_mentions))

        if message_reference is not None:
            body.put("message_reference", attrs.asdict(message_reference))

        if components is not None:
            self._apply_components(body, components)

        if sticker_ids is not None:
            body.put("sticker_ids", sticker_ids)

        if files is not None:
            body.put("files", files)

        if payload_json is not None:
            body.put("payload_json", payload_json)

        if attachments is not None:
            body.put("attachments", attachments)

        if flags is not None:
            body.put("flags", flags)

        return body

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
        attachments: List[Any] = None,
        flags: int = None,
        thread_name: str = None
    ) -> None:
        payload = self._build_payload(
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
        payload.put("thread_name", thread_name)

        await self.http.send_request(
            CREATE_WEBHOOK.method,
            webhook_url,
            data=payload
        )

    async def create_webhook(self, channel_id: int, name: str, avatar: str = None, reason: str = None) -> Webhook:
        headers = {}

        if reason is not None:
            headers.update({"X-Audit-Log-Reason": reason})

        payload = {"name": name, "avatar": avatar}
        webhook_data = await self.http.send_request(
            CREATE_WEBHOOK.method,
            CREATE_WEBHOOK.uri.url_string.format(channel_id=channel_id),
            headers=headers,
            data=payload
        )
        return Webhook(**await webhook_data.json())

    async def fetch_emoji(self, guild_id: int, emoji: str) -> Emoji:
        if re.match(r"<:(\w+):(\w+)>", emoji):
            emoji_name, emoji_id = emoji.replace(">", "").replace("<", "").split(":")[1:]
            url = GET_GUILD_EMOJI.uri.url_string.format(guild_id=guild_id, emoji_id=emoji_id)
            response = await self.http.send_request(
                GET_GUILD_EMOJI.method,
                url=url,
                content_type=self.http.APPLICATION_X_WWW_FORM_URLENCODED
            )

            return Emoji(**await response.json())

        return Emoji(name=emoji, id=Snowflake())  # type: ignore

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
            headers.update({"X-Audit-Log-Reason": reason})

        await self.http.send_request(
            CREATE_REACTION.method,
            url=CREATE_REACTION.uri.url_string.format(
                channel_id=channel_id,
                message_id=message_id,
                emoji=self._parse_emoji(emoji)
            ),
            headers=headers,
            content_type=self.http.APPLICATION_X_WWW_FORM_URLENCODED
        )

        return emoji

    async def delete_message(self, channel_id: int, message_id: int, reason: str = None) -> None:
        headers = {}

        if reason is not None:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.http.send_request(
            DELETE_MESSAGE.method,
            DELETE_MESSAGE.uri.url_string.format(channel_id=channel_id, message_id=message_id),
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
        attachments: List | None = None,
        flags: int | None = None
    ) -> Message:
        payload = self._build_payload(
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

        data = await self.http.send_request(
            CREATE_MESSAGE.method,
            CREATE_MESSAGE.uri.url_string.format(channel_id),
            data=payload
        )
        message_json = await data.json()
        return Message(**message_json)

    async def fetch_guild(self, guild_id: int, with_counts: bool = False) -> Guild:
        url_with_guild_id = GET_GUILD.uri.url_string.format(guild_id=guild_id)
        build_guild_url = (
            url_with_guild_id
            if not with_counts
            else url_with_guild_id + "?with_counts=true"
        )
        data = await self.http.send_request(
            GET_GUILD.method, build_guild_url
        )
        guild_data = await data.json()
        return Guild(**guild_data)

    async def delete_guild(self, guild_id: int) -> None:
        await self.http.send_request(
            DELETE_GUILD.method,
            url=DELETE_GUILD.uri.url_string.format(guild_id=guild_id)
        )

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
        payload = {'name': name, 'system_channel_flags': system_channel_flags}

        if region is not None:
            payload.update({"region": region})

        if icon is not None:
            payload.update({"icon": icon})

        if verification_level is not None:
            payload.update({"verification_level": verification_level})

        if default_message_notifications is not None:
            payload.update({"default_message_notifications": default_message_notifications})

        if explicit_content_filter is not None:
            payload.update({"explicit_content_filter": explicit_content_filter})

        if roles is not None:
            payload.update({"roles": roles})

        if channels is not None:
            payload.update({"channels": channels})

        if afk_channel_id is not None:
            payload.update({"afk_channel_id": afk_channel_id})

        if afk_timeout is not None:
            payload.update({"afk_timeout": afk_timeout})

        if system_channel_id is not None:
            payload.update({"system_channel_id": system_channel_id})

        data = await self.http.send_request(
            CREATE_GUILD.method,
            CREATE_GUILD.uri.url_string,
            data=payload
        )
        return Guild(**await data.json())

    async def create_guild_ban(
        self,
        guild_id: int | Snowflake,
        member_id: int | Snowflake,
        reason: str,
        delete_message_days: int,
        delete_message_seconds: int
    ) -> None:
        payload = {
            'delete_message_days': delete_message_days,
            'delete_message_seconds': delete_message_seconds
        }
        headers = {}
        url = CREATE_GUILD_BAN.uri.url_string.format(guild_id=guild_id, user_id=member_id)

        if delete_message_days > 0:
            warnings.warn("Option \"delete_message_days\" deprecated in Discord API", category=DeprecationWarning)

        if reason is not None:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.http.send_request(
            CREATE_GUILD_BAN.method,
            url=url,
            headers=headers,
            data=payload
        )

    async def create_interaction_response(
        self, interaction_type: InteractionCallbackType,
        interaction_data: InteractionCallbackData, interaction_id: int,
        interaction_token: str
    ) -> None:
        payload = {
            "type": interaction_type.value,
            "data": attrs.asdict(interaction_data)
        }

        await self.http.send_request(
            CREATE_INTERACTION_RESPONSE.method,
            url=CREATE_INTERACTION_RESPONSE.uri.url_string.format(
                interaction_id=interaction_id,
                interaction_token=interaction_token
            ),
            data=payload
        )

    async def fetch_message(self, channel_id: int, message_id: int) -> Message:
        raw_message = await self.http.send_request(
            GET_MESSAGE.method,
            url=GET_MESSAGE.uri.url_string.format(
                channel_id=channel_id,
                message_id=message_id
            )
        )

        return Message(**await raw_message.json())

    async def create_application_command(
        self,
        application_id: int,
        name: str,
        description: str,
        default_permissions: bool = False,
        dm_permissions: bool = False,
        default_member_permissions: str = None,
        guild_id: int | None = None,
        options: List[SlashOption] = None,
        nsfw: bool = False
    ) -> None:
        payload = {"name": name, "description": description}

        if default_permissions:
            payload.update({"default_permissions": default_permissions})

        if dm_permissions:
            payload.update({"dm_permissions": dm_permissions})

        if default_member_permissions is not None:
            payload.update({"default_member_permissions": default_member_permissions})

        if guild_id is not None:
            payload.update({"guild_id": guild_id})

        if options is not None:
            payload.update({"options": [option.as_json() for option in options]})

        if nsfw:
            payload.update({"nsfw": nsfw})

        await self.http.send_request(
            CREATE_APPLICATION_COMMAND.method,
            url=CREATE_APPLICATION_COMMAND.uri.url_string.format(application_id=application_id),
            data=payload
        )

    async def fetch_initial_interaction_response(self, application_id: int, interaction_token: str) -> Message:
        url = GET_ORIGINAL_INTERACTION_RESPONSE.uri.url_string.format(
            application_id=application_id,
            interaction_token=interaction_token
        )
        response = await self.http.send_request(
            GET_ORIGINAL_INTERACTION_RESPONSE.method,
            url=url
        )

        return Message(**await response.json())

    async def edit_message(
        self,
        channel_id: Snowflake | int,
        message_id: Snowflake | int,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        flags: int | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: ActionRow | None = None
    ) -> Message:  # TODO: File uploading later
        payload = self._build_payload(
            content=content,
            embeds=embeds,
            embed=embed,
            flags=flags,
            allowed_mentions=allowed_mentions,
            components=components
        )

        url = EDIT_MESSAGE.uri.url_string.format(
            channel_id=channel_id, message_id=message_id
        )
        response = await self.http.send_request(
            EDIT_MESSAGE.method,
            url=url,
            data=payload
        )

        return Message(**await response.json())

    async def delete_all_reactions(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        url = DELETE_ALL_REACTIONS.uri.url_string.format(channel_id=channel_id, message_id=message_id)
        await self.http.send_request(
            DELETE_ALL_REACTIONS.method,
            url=url,
            headers={}
        )

    async def delete_all_reactions_for_emoji(
        self,
        guild_id: Snowflake | int,
        channel_id: Snowflake | int,
        message_id: Snowflake | int,
        emoji: str | Snowflake | Emoji
    ):
        parsed_emoji = self._parse_emoji(await self.fetch_emoji(guild_id=guild_id, emoji=emoji))
        url = DELETE_ALL_REACTION_FOR_EMOJI.uri.url_string.format(
            channel_id=channel_id, message_id=message_id, emoji=parsed_emoji
        )
        await self.http.send_request(
            DELETE_ALL_REACTION_FOR_EMOJI.method, url=url,
            content_type=self.http.APPLICATION_X_WWW_FORM_URLENCODED
        )

    async def edit_original_interaction_response(
        self,
        application_id: int | Snowflake,
        interaction_token: str,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: ActionRow | None = None,
        files: List[Any] | None = None,
        payload_json: str | None = None,
        attachments: Any | None = None,
        thread_id: int | Snowflake | None = None
    ) -> Message:
        url = EDIT_ORIGINAL_INTERACTION_RESPONSE.uri.url_string.format(
            application_id=application_id, interaction_token=interaction_token
        )
        payload = self._build_payload(
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

        response = await self.http.send_request(
            EDIT_ORIGINAL_INTERACTION_RESPONSE.method, url=url, data=payload
        )
        return Message(**await response.json())

    async def fetch_invite(
        self,
        invite_code: str,
        with_counts: bool = False,
        with_expiration: bool = False,
        guild_scheduled_event_id: Snowflake | None = None
    ) -> Invite:
        url = self.build_url(
            route=GET_INVITE,
            data={"invite_code": invite_code},
            query_params={
                "with_counts": with_counts,
                "with_expiration": with_expiration,
                "guild_scheduled_event_id": guild_scheduled_event_id
            }
        )

        response = await self.http.send_request(
            GET_INVITE.method, url=url
        )

        return Invite(**await response.json())

    async def delete_invite(self, invite_code: str, reason: str | None = None) -> Invite:
        url = DELETE_INVITE.uri.url_string.format(invite_code=invite_code)
        headers = {}

        if reason is not None:
            headers['X-Audit-Log-Reason'] = reason

        response = await self.http.send_request(
            DELETE_INVITE.method, url=url,
            headers=headers
        )

        return Invite(**await response.json())

    async def fetch_guild_invites(self, guild_id: Snowflake) -> List:
        url = self.build_url(
            route=GET_GUILD_INVITES,
            data={"guild_id": guild_id}
        )
        # Integration object later
        return await (await self.http.send_request(
            GET_GUILD_INVITES.method, url=url
        )).json()

    @staticmethod
    def _parse_emoji(emoji: str | Emoji | Snowflake | int) -> str:
        return str(emoji).replace("<", "").replace(">", "") if emoji.emoji_id > 0 else emoji

    @staticmethod
    def _apply_components(payload: MutableJsonBuilder, components: ActionRow):
        payload.put(
            "components", [{"type": ActionRow.INTERACTION_TYPE, "components": []}]
        )
        for component in components.components:
            for row in payload.get("components"):
                message_components = row.get("components")
                message_components.append(component.as_json())  # type: ignore

    @staticmethod
    def build_url(route: Route, data: Dict[str, Any] = None, query_params: Dict[str, Any] = None) -> str:
        url = route.uri.url_string.format(**data) \
            if data is not None else route.uri.url_string

        if query_params is not None:
            for param, value in query_params.items():
                url += f"?{param}={value}"

        return url
