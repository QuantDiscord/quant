from typing import List

from dispy.components.action_row import ActionRow
from dispy.data.guild.messages.embeds import Embed
from dispy.data.guild.messages.mentions import AllowedMentions
from dispy.data.guild.messages.message import Message


class BaseContext:
    def __init__(self, client, message: Message) -> None:
        self.original_message = message
        self.client = client

    async def send_message(
        self,
        channel_id: int = None,
        content: str = None,
        nonce: str | int = None,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        message_reference=None,
        components: List[ActionRow] = None,
        sticker_ids: List = None,
        files=None,
        payload_json: str = None,
        attachments: List = None,
        flags: int = None
    ) -> None:
        await self.client.rest.create_message(
            channel_id=channel_id if channel_id is not None else self.original_message.channel_id,
            content=content,
            nonce=nonce,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            components=[component.as_json() for component in components if len(components) > 0],
            sticker_ids=sticker_ids,
            files=files,
            payload_json=payload_json,
            attachments=attachments,
            flags=flags
        )


class MessageCommandContext(BaseContext):
    ...
