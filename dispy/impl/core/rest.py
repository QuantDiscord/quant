import re

import attrs

from typing import List, Any

from dispy.api.core.rest_aware import RESTAware
from dispy.data.gateway.snowflake import Snowflake
from dispy.data.guild.guild_object import Guild
from dispy.data.guild.messages.emoji import Emoji
from dispy.data.guild.messages.mentions import AllowedMentions
from dispy.impl.core.http_manager import HttpManager
from dispy.data.route import (
    CREATE_MESSAGE, DELETE_MESSAGE,
    CREATE_WEBHOOK, GET_GUILD, CREATE_GUILD,
    DELETE_GUILD, CREATE_REACTION, GET_GUILD_EMOJI
)
from dispy.data.guild.messages.message import Message
from dispy.data.guild.messages.embeds import Embed
from dispy.data.guild.webhooks.webhook import Webhook


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
            headers={"Content-Type": self.http.APPLICATION_JSON}
        )

    async def create_webhook(self, channel_id: int, name: str, avatar: str = None, reason: str = None) -> Webhook:
        headers = {self.http.AUTHORIZATION: self.token, "Content-Type": self.http.APPLICATION_JSON}

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
        emoji: str | Emoji,
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

        if isinstance(emoji, Emoji):
            emoji = str(await self.fetch_emoji(guild_id=guild_id, emoji=str(emoji)))

        if reason is not None:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.http.send_request(
            CREATE_REACTION.method,
            url=CREATE_REACTION.uri.url_string.format(
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji
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
        components: List = None,
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
            payload.update({"components": components})

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
                self.http.AUTHORIZATION: self.token, "Content-Type": self.http.APPLICATION_JSON
            }
        )
        message_json = await data.json()
        return Message(**message_json)

    async def fetch_guild(self, guild_id: int, with_counts: bool = False) -> Guild:
        headers = {self.http.AUTHORIZATION: self.token, "Content-Type": self.http.APPLICATION_JSON}
        get_guild_url = GET_GUILD.uri.url_string.format(guild_id=guild_id) \
            if not with_counts else GET_GUILD.uri.url_string.format(guild_id=guild_id) + "?with_counts=true"
        data = await self.http.send_request(
            GET_GUILD.method, get_guild_url,
            headers=headers
        )
        guild_data = await data.json()
        return Guild(**guild_data)

    async def delete_guild(self, guild_id: int) -> None:
        headers = {self.http.AUTHORIZATION: self.token, "Content-Type": self.http.APPLICATION_JSON}
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
        headers = {self.http.AUTHORIZATION: self.token, "Content-Type": self.http.APPLICATION_JSON}

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
