import re
from typing import List, Any, Dict

import attrs

from quant.data.guild.messages.interactions.slashes.slash_option import SlashOption
from quant.api.core.rest_aware import RESTAware
from quant.data.gateway.snowflake import Snowflake
from quant.data.guild.guild_object import Guild
from quant.data.guild.messages.emoji import Emoji
from quant.data.guild.messages.interactions.response.interaction_callback_data import InteractionCallbackData
from quant.data.guild.messages.interactions.response.interaction_callback_type import InteractionCallbackType
from quant.data.guild.messages.mentions import AllowedMentions
from quant.impl.core.http_manager import HttpManager
from quant.data.route import (
    CREATE_MESSAGE, DELETE_MESSAGE,
    CREATE_WEBHOOK, GET_GUILD, CREATE_GUILD,
    DELETE_GUILD, CREATE_REACTION, GET_GUILD_EMOJI,
    CREATE_INTERACTION_RESPONSE, GET_MESSAGE,
    CREATE_APPLICATION_COMMAND
)
from quant.data.guild.messages.message import Message
from quant.data.guild.messages.embeds import Embed
from quant.data.guild.webhooks.webhook import Webhook


class DiscordREST(RESTAware):
    def __init__(self, token: str) -> None:
        self.http = HttpManager()
        self.token = token

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
        payload = {}

        if components is not None:
            payload.update({"components": components})

        if files is not None:
            payload.update({"files": files})

        if payload_json is not None:
            payload.update({"payload_json": payload_json})

        if attachments is not None:
            payload.update({"attachments": attachments})

        if flags is not None:
            payload.update({"flags": flags})

        if thread_name is not None:
            payload.update({"thread_name": thread_name})

        if content is not None:
            payload.update({"content": content})

        if username is not None:
            payload.update({"username": username})

        if avatar_url is not None:
            payload.update({"avatar_url": avatar_url})

        if tts is not None:
            payload.update({"tts": tts})

        if embed is not None:
            payload.update({"embeds": [embed]})

        if embeds is not None:
            payload.update({"embeds": embeds})

        if allowed_mentions is not None:
            payload.update({"allowed_mentions": attrs.asdict(allowed_mentions)})

        await self.http.send_request(
            CREATE_WEBHOOK.method,
            webhook_url,
            data=payload,
            headers={}
        )

    async def create_webhook(self, channel_id: int, name: str, avatar: str = None, reason: str = None) -> Webhook:
        headers = {self.http.AUTHORIZATION: self.token, }

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
        headers = {self.http.AUTHORIZATION: self.token, 'Content-Type': self.http.APPLICATION_X_WWW_FORM_URLENCODED}

        if re.match(r"<:(\w+):(\w+)>", emoji):
            emoji_name, emoji_id = (
                emoji.replace(">", "").replace("<", "")
            ).split(":")[1:]
            url = GET_GUILD_EMOJI.uri.url_string.format(guild_id=guild_id, emoji_id=emoji_id)
            response = await self.http.send_request(GET_GUILD_EMOJI.method, url=url, headers=headers)

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
        """
        :param emoji:
        :param guild_id:
        :param channel_id:
        :param message_id:
        :param reason:
        :return:
        """
        headers = {self.http.AUTHORIZATION: self.token, 'Content-Type': self.http.APPLICATION_X_WWW_FORM_URLENCODED}
        emoji = await self.fetch_emoji(guild_id=guild_id, emoji=emoji)

        if reason is not None:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.http.send_request(
            CREATE_REACTION.method,
            url=CREATE_REACTION.uri.url_string.format(
                channel_id=channel_id,
                message_id=message_id,
                emoji=str(emoji).replace("<", "").replace(">", "") if emoji.emoji_id > 0 else emoji
            ),
            headers=headers
        )

        return emoji

    async def delete_message(self, channel_id: int, message_id: int, reason: str = None) -> None:
        headers = {self.http.AUTHORIZATION: self.token}

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
        content: str = None,
        nonce: str | int = None,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        message_reference=None,
        components: List[Dict[str, Any]] = None,
        sticker_ids: List = None,
        files=None,
        payload_json: str = None,
        attachments: List = None,
        flags: int = None
    ):
        payload = {}

        if content is not None:
            payload.update({"content": str(content)})

        if nonce is not None:
            payload.update({"nonce": nonce})

        if tts is not None:
            payload.update({"tts": tts})

        if embed is not None:
            payload.update({"embeds": [embed]})

        if embeds is not None:
            payload.update({"embeds": embeds})

        if sticker_ids is not None:
            payload.update({"sticker_ids": sticker_ids})

        if files is not None:
            payload.update({"files": files})

        if payload_json is not None:
            payload.update({"payload_json": payload_json})

        if components is not None:
            payload.update({"components": []})
            for component in components:
                message_components = payload.get("components")
                message_components.append(component)  # type: ignore

        if flags is not None:
            payload.update({"flags": flags})

        if attachments is not None:
            payload.update({"attachments": attachments})

        if allowed_mentions is not None:
            payload.update({"allowed_mentions": attrs.asdict(allowed_mentions)})

        if message_reference is not None:
            payload.update({"message_reference": message_reference})

        data = await self.http.send_request(
            CREATE_MESSAGE.method, CREATE_MESSAGE.uri.url_string.format(channel_id),
            data=payload, headers={
                self.http.AUTHORIZATION: self.token,
            }
        )
        message_json = await data.json()
        return Message(**message_json)

    async def fetch_guild(self, guild_id: int, with_counts: bool = False) -> Guild:
        headers = {self.http.AUTHORIZATION: self.token, }
        url_with_guild_id = GET_GUILD.uri.url_string.format(guild_id=guild_id)
        get_guild_url = (
            url_with_guild_id
            if not with_counts
            else url_with_guild_id + "?with_counts=true"
        )
        data = await self.http.send_request(
            GET_GUILD.method, get_guild_url,
            headers=headers
        )
        guild_data = await data.json()
        return Guild(**guild_data)

    async def delete_guild(self, guild_id: int) -> None:
        headers = {self.http.AUTHORIZATION: self.token, }
        await self.http.send_request(
            DELETE_GUILD.method,
            url=DELETE_GUILD.uri.url_string.format(guild_id=guild_id),
            headers=headers
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
        headers = {self.http.AUTHORIZATION: self.token, }

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
            headers=headers,
            data=payload
        )
        return Guild(**await data.json())

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
            headers={},
            data=payload
        )

    async def fetch_message(self, channel_id: int, message_id: int) -> Message:
        raw_message = await self.http.send_request(
            GET_MESSAGE.method,
            url=GET_MESSAGE.uri.url_string.format(
                channel_id=channel_id,
                message_id=message_id
            ),
            headers={self.http.AUTHORIZATION: self.token}
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
            data=payload,
            headers={
                self.http.AUTHORIZATION: self.token
            }
        )
