import attrs

from typing import List, Any

from dispy.api.core.rest_aware import RESTAware
from dispy.data.guild.messages.mentions.allowed_mentions import AllowedMentions
from dispy.impl.core.http_manager import HttpManager
from dispy.data.route import CREATE_MESSAGE, DELETE_MESSAGE, CREATE_WEBHOOK
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

        await self.http.send_request("POST", webhook_url,
                                     data=payload, headers={"Content-Type": self.http.APPLICATION_JSON})

    async def create_webhook(self, channel_id: int, name: str, avatar: str = None, reason: str = None) -> Webhook:
        headers = {self.http.AUTHORIZATION: self.token, "Content-Type": self.http.APPLICATION_JSON}

        if reason is not None:
            headers.update({"X-Audit-Log-Reason": reason})

        payload = {"name": name, "avatar": avatar}
        webhook_data = await self.http.send_request("POST", CREATE_WEBHOOK.format(channel_id=channel_id),
                                                    headers=headers, data=payload)
        return Webhook(**await webhook_data.json())

    async def delete_message(self, channel_id: int, message_id: int, reason: str = None) -> None:
        headers = {self.http.AUTHORIZATION: self.token}

        if reason is not None:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.http.send_request("DELETE", DELETE_MESSAGE.format(channel_id=channel_id, message_id=message_id),
                                     headers=headers)

    async def create_message(
        self,
        channel_id: int,
        content: str = None, *,
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
            "POST", CREATE_MESSAGE.format(channel_id),
            data=payload, headers={
                self.http.AUTHORIZATION: self.token, "Content-Type": self.http.APPLICATION_JSON
            }
        )
        message_json = await data.json()

        return Message(**message_json)
