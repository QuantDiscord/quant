from typing import List, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quant.impl.core.client import Client
    from quant.entities.interactions.interaction import Interaction
    from quant.entities.message import Message
    from quant.entities.button import Button

from quant.entities.action_row import ActionRow
from quant.entities.embeds import Embed
from quant.entities.allowed_mentions import AllowedMentions


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
            components = [self.client.gateway.event_factory for component in components]

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


class InteractionContext:
    def __init__(self, client, interaction) -> None:
        self.client: Client = client
        self.interaction: Interaction = interaction


class ButtonContext(InteractionContext):
    def __init__(self, client, interaction, button) -> None:
        self.button: Button = button
        super().__init__(client, interaction)


class ModalContext(InteractionContext):
    def __init__(self, client, interaction) -> None:
        self.values = [
            interaction.interaction_data.components.components[i]['components'][0]['value']
            for i in range(len(interaction.interaction_data.components.components))
        ]

        super().__init__(client, interaction)
