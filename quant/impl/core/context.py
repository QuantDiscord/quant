from typing import List, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quant.impl.core.client import Client
    from quant.data.guild.messages.interactions.interaction import Interaction
    from quant.data.guild.messages.message import Message

from quant.data.components.action_row import ActionRow
from quant.data.guild.messages.embeds import Embed
from quant.data.guild.messages.mentions import AllowedMentions


class BaseContext:
    def __init__(self, client, message) -> None:
        self.original_message: Message = message
        self.client: Client = client

    async def send_message(
        self,
        channel_id: int = None,
        content: Any = None,
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
    ):
        if components is not None:
            components = [component.as_json() for component in components]

        return await self.client.rest.create_message(
            channel_id=channel_id if channel_id is not None else self.original_message.channel_id,
            content=str(content),
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


class MessageCommandContext(BaseContext):
    ...


class InteractionContext:
    def __init__(self, client, interaction) -> None:
        self.client: Client = client
        self.interaction: Interaction = interaction


class CombineContext(BaseContext):
    def __init__(self, client, original_message=None, interaction=None) -> None:
        self.client: Client = client
        self.original_message: Message = original_message
        self.interaction: Interaction = interaction
        super().__init__(self.client, self.original_message)

    async def send_message(
        self,
        channel_id: int = None,
        content: Any = None,
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
    ):
        if hasattr(self, 'interaction'):
            return await self.interaction.respond(
                content=content,
                tts=tts,
                embed=embed,
                embeds=embeds,
                allowed_mentions=allowed_mentions,
                flags=flags,
                components=components,
                attachments=attachments
            )

        if components is not None:
            components = [component.as_json() for component in components]

        return await self.client.rest.create_message(
            channel_id=channel_id if channel_id is not None else self.original_message.channel_id,
            content=str(content),
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
