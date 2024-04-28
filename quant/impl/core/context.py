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

from typing import List, TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from quant.impl.core.client import Client
    from quant.entities.interactions.interaction import Interaction
    from quant.entities.message import Message, MessageReference, MessageFlags
    from quant.entities.button import Button
    from quant.entities.user import User
    from quant.entities.member import GuildMember
    from quant.entities.action_row import ActionRow
    from quant.entities.modal.modal import ModalInteractionCallbackData
    from quant.entities.modal.text_input import TextInput
    from quant.entities.modal.modal import Modal

from quant.entities.message import Attachment
from quant.impl.files import AttachableURL, File
from quant.entities.snowflake import Snowflake
from quant.entities.roles import GuildRole
from quant.entities.channel import TextChannel, VoiceChannel, Thread
from quant.entities.interactions.choice_response import InteractionDataOption
from quant.entities.embeds import Embed
from quant.entities.allowed_mentions import AllowedMentions
from quant.utils.parser import parse_option_type

AttachmentT = TypeVar("AttachmentT", bound=AttachableURL | File | Attachment)


class BaseContext:
    def __init__(self, client, message) -> None:
        self.original_message: Message = message
        self.client: Client = client

    @property
    def author(self) -> User:
        return self.original_message.author

    async def send_message(
        self,
        channel_id: int = None,
        content: Any = None,
        nonce: str | int = None,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        message_reference: MessageReference | None = None,
        components: ActionRow | None = None,
        sticker_ids: List = None,
        files=None,
        payload_json: str = None,
        attachments: List[AttachmentT] = None,
        flags: MessageFlags | int | None = None
    ) -> Message:
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


OptionT = TypeVar("OptionT", bound=InteractionDataOption | None)
ChannelT = TypeVar("ChannelT", bound=TextChannel | VoiceChannel | Thread)


class InteractionContext:
    def __init__(self, client: Client, interaction: Interaction) -> None:
        self.client = client
        self.interaction = interaction

    @property
    def guild_id(self) -> Snowflake | int:
        return self.interaction.guild_id

    @property
    def author(self) -> GuildMember:
        return self.interaction.member

    async def get_option(self, name: str) -> OptionT:
        interaction_options = self.interaction.data.options
        if interaction_options is None:
            return

        options = list(filter(lambda x: x.name.lower() == name.lower(), interaction_options))
        if len(options) == 0:
            return

        option = options[0]
        return await parse_option_type(self.client, self.interaction, option.type, option.value)

    async def get_user_option(self, name: str) -> User | None:
        return await self.get_option(name=name)

    async def get_channel_option(self, name: str) -> ChannelT | None:
        return await self.get_option(name=name)

    async def get_role_option(self, name: str) -> GuildRole | None:
        return await self.get_option(name=name)

    async def respond(
        self,
        content: str | Any | None = None,
        tts: bool = False,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        flags: MessageFlags | int = 0,
        components: ActionRow = None,
        attachments: List[AttachmentT] = None
    ) -> None:
        await self.interaction.respond(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            flags=flags,
            components=components,
            attachments=attachments
        )

    async def respond_modal(self, modal: Modal) -> None:
        await self.interaction.respond_modal(modal=modal)


class ButtonContext(InteractionContext):
    def __init__(self, client, interaction, button) -> None:
        self.button: Button = button
        super().__init__(client, interaction)


class ModalContext(InteractionContext):
    def __init__(self, client: Client, interaction: Interaction) -> None:
        self.values = {}

        interaction_data: ModalInteractionCallbackData = interaction.data
        for action_row in interaction_data.components:
            for component in action_row.components:
                component: TextInput = component
                self.values[component.custom_id] = component.value

        super().__init__(client, interaction)
