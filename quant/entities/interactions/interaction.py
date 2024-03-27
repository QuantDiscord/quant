"""
MIT License

Copyright (c) 2023 MagM1go

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

import enum
from typing import Any, List, TYPE_CHECKING, Dict

import attrs

if TYPE_CHECKING:
    from ..action_row import ActionRow
    from quant.entities.message import Message, Attachment
    from quant.entities.guild import Guild
    from quant.entities.modal.modal import Modal, ModalInteractionCallbackData

from quant.entities.message_flags import MessageFlags
from .choice_response import InteractionDataOption
from ..message import Message
from ..channel import Channel
from .application_command import ApplicationCommandOptionType
from quant.entities.snowflake import Snowflake
from quant.entities.user import User
from quant.entities.interactions.component_types import ComponentType
from quant.entities.embeds import Embed
from quant.entities.allowed_mentions import AllowedMentions
from quant.entities.member import GuildMember
from quant.entities.model import BaseModel


class InteractionCallbackType(enum.Enum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9
    PREMIUM_REQUIRED = 10


class InteractionType(enum.Enum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


@attrs.define(kw_only=True, hash=True)
class InteractionCallbackData(BaseModel):
    tts: bool = attrs.field()
    content: str | None = attrs.field()
    embeds: List[Embed] | None = attrs.field()
    allowed_mentions: AllowedMentions | None = attrs.field()
    flags: MessageFlags | int | None = attrs.field()
    components: ActionRow | None = attrs.field()
    attachments: List[Attachment] | None = attrs.field()


@attrs.define(kw_only=True, hash=True)
class InteractionData(BaseModel):
    id: Snowflake = attrs.field(default=0)
    component_type: ComponentType = attrs.field(default=0)
    type: int = attrs.field(default=None)
    custom_id: str = attrs.field(default=None)
    name: str = attrs.field(default=None)
    option_type: ApplicationCommandOptionType = attrs.field(default=0)
    guild_id: int | Snowflake | None = attrs.field(default=None)
    value: str | int | bool = attrs.field(default=None)
    options: List[InteractionDataOption] = attrs.field(default=None)
    focused: bool = attrs.field(default=False)
    components: ActionRow = attrs.field(default=None)
    resolved: Dict = attrs.field(default=None)


@attrs.define(kw_only=True, hash=True)
class InteractionResponse(BaseModel):
    interaction_response_type: InteractionCallbackType = attrs.field(default=InteractionCallbackType.PONG, alias="type")
    interaction_response_data: InteractionCallbackData = attrs.field(default=None)


@attrs.define(kw_only=True, hash=True)
class Interaction(BaseModel):
    name: str = attrs.field(default=None)
    id: Snowflake = attrs.field(default=0)
    application_id: Snowflake = attrs.field(default=0)
    type: InteractionType = attrs.field(
        default=InteractionType.PING,
        converter=InteractionType
    )
    data: InteractionData | ModalInteractionCallbackData = attrs.field(default=None)
    guild_id: Snowflake = attrs.field(default=0)
    channel: Channel = attrs.field(default=None)
    channel_id: Snowflake = attrs.field(default=0)
    member: GuildMember | None = attrs.field(default=None)
    user: User | None = attrs.field(default=None)
    token: str = attrs.field(default=None)
    version: int = attrs.field(default=-1)
    app_permissions: str = attrs.field(default=None)
    locale: str = attrs.field(default=None)
    guild_locale: str = attrs.field(default=None)
    entitlements: List[Any] = attrs.field(default=None)
    entitlement_sku_ids: Any = attrs.field(default=None)
    message: Message = attrs.field(default=None)
    guild: Guild = attrs.field(default=None)
    _authorizing_integration_owners: Any = attrs.field(default=None)

    async def respond(
        self,
        content: str | Any | None = None,
        tts: bool = False,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        flags: MessageFlags | int = 0,
        components: ActionRow = None,
        attachments: List[Attachment] = None
    ) -> None:
        if embed is not None:
            embeds = [embed]

        if isinstance(flags, MessageFlags):
            flags = flags.value

        await self.client.rest.create_interaction_response(
            InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
            InteractionCallbackData(
                content=str(content) if content is not None else None,
                tts=tts,
                embeds=embeds,
                allowed_mentions=allowed_mentions,
                flags=flags,
                components=components,
                attachments=attachments
            ),
            self.id,
            self.token
        )

    async def respond_modal(self, modal: Modal):
        from quant.entities.modal.modal import ModalInteractionCallbackData

        await self.client.rest.create_interaction_response(
            InteractionCallbackType.MODAL,
            ModalInteractionCallbackData(
                custom_id=modal.custom_id,
                title=modal.title,
                components=modal.components
            ),
            self.id,
            self.token
        )

    async def fetch_initial_response(self):
        return await self.client.rest.fetch_initial_interaction_response(
            self.client.client_id, self.token
        )

    async def edit_interaction(
        self,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: ActionRow | None = None,
        files: List[Any] | None = None,
        payload_json: str | None = None,
        attachments: List[Attachment] | None = None
    ) -> Message:
        return await self.client.rest.edit_original_interaction_response(
            application_id=self.client.client_id,
            interaction_token=self.token,
            content=content,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            files=files,
            payload_json=payload_json,
            attachments=attachments
        )

    async def deferred(self, flags: MessageFlags | int | None = None) -> None:
        await self.client.rest.create_interaction_response(
            interaction_type=InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
            interaction_data=InteractionCallbackData(
                tts=False,
                content=None,
                embeds=None,
                allowed_mentions=None,
                flags=flags,
                components=None,
                attachments=None
            ),
            interaction_id=self.id,
            interaction_token=self.token
        )
        await self.client.rest.create_followup_message(
            application_id=self.application_id,
            interaction_token=self.token,
            flags=flags,
        )
