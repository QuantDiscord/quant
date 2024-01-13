import enum
from typing import Any, List, TYPE_CHECKING, Dict

import attrs

if TYPE_CHECKING:
    from quant.entities.message import Message

from ..action_row import ActionRow
from quant.entities.message_flags import MessageFlags
from .choice_response import ChoiceResponse
from ..message import Message
from ..channel import Channel
from .application_command_option import ApplicationCommandOptionType
from quant.entities.modal.modal import ModalInteractionCallbackData
from quant.entities.snowflake import Snowflake
from quant.entities.user import User
from quant.entities.modal.modal import Modal
from quant.entities.embeds import Embed
from quant.entities.allowed_mentions import AllowedMentions
from quant.entities.member import GuildMember
from quant.entities.model import BaseModel
from quant.utils.attrs_extensions import execute_converters


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


@attrs.define(kw_only=True, field_transformer=execute_converters)
class InteractionCallbackData(BaseModel):
    tts: bool = attrs.field(default=False)
    content: str = attrs.field(default=None)
    embeds: List[Embed] = attrs.field(default=None)
    allowed_mentions: AllowedMentions = attrs.field(default=None)
    flags: int = attrs.field(default=0)
    components: ActionRow = attrs.field(default=None)
    attachments: Any = attrs.field(default=None)


@attrs.define(kw_only=True, field_transformer=execute_converters)
class InteractionData(BaseModel):
    interaction_id: Snowflake = attrs.field(default=0, alias="id")
    component_type: int = attrs.field(default=0)
    interaction_type: int = attrs.field(default=None, alias="type")
    custom_id: str = attrs.field(default=None)
    name: str = attrs.field(default=None)
    option_type: ApplicationCommandOptionType = attrs.field(default=0)
    guild_id: int | Snowflake | None = attrs.field(default=None)
    value: str | int | bool = attrs.field(default=None)
    options: List[ChoiceResponse] = attrs.field(default=None)
    focused: bool = attrs.field(default=False)
    components: ActionRow = attrs.field(default=None)
    resolved: Dict = attrs.field(default=None)


@attrs.define(kw_only=True)
class InteractionResponse(BaseModel):
    interaction_response_type: InteractionCallbackType = attrs.field(default=InteractionCallbackType.PONG, alias="type")
    interaction_response_data: InteractionCallbackData = attrs.field(default=None)


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Interaction(BaseModel):
    interaction_name: str = attrs.field(alias="name", default=None)
    interaction_id: Snowflake = attrs.field(alias="id", default=0)
    application_id: Snowflake = attrs.field(default=0)
    interaction_type: InteractionType = attrs.field(
        alias="type",
        default=InteractionType.PING,
        converter=InteractionType
    )
    interaction_data: InteractionData = attrs.field(alias="data", default=None)
    guild_id: Snowflake = attrs.field(default=0)
    channel: Channel = attrs.field(default=None)
    channel_id: Snowflake = attrs.field(default=0)
    member: GuildMember | None = attrs.field(default=None)
    user: User | None = attrs.field(default=None)
    interaction_token: str = attrs.field(default=None, alias="token")
    version: int = attrs.field(default=-1)
    app_permissions: str = attrs.field(default=None)
    locale: str = attrs.field(default=None)
    guild_locale: str = attrs.field(default=None)
    entitlements: List[Any] = attrs.field(default=None)
    entitlement_sku_ids: Any = attrs.field(default=None)
    message: Message = attrs.field(default=None)
    _guild: Any = attrs.field(default=None, repr=False, alias="guild")
    _authorizing_integration_owners: Any = attrs.field(default=None, alias="authorizing_integration_owners")

    async def respond(
        self,
        content: str | Any | None = None,
        tts: bool = False,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        flags: MessageFlags | int = 0,
        components: ActionRow = None,
        attachments: List[Any] = None
    ) -> None:
        if embed is not None:
            embeds = [embed]

        await self.client.rest.create_interaction_response(
            InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
            InteractionCallbackData(
                content=str(content) if content is not None else None,
                tts=tts,
                embeds=embeds,
                allowed_mentions=allowed_mentions,
                flags=flags if flags is None or isinstance(flags, int) else flags.value,
                components=components,
                attachments=attachments
            ),
            self.interaction_id,
            self.interaction_token
        )

    async def respond_modal(self, modal: Modal):
        await self.client.rest.create_interaction_response(
            InteractionCallbackType.MODAL,
            ModalInteractionCallbackData(
                custom_id=modal.custom_id,
                title=modal.title,
                components=[ActionRow([component.components for component in modal.components])]
            ),
            self.interaction_id,
            self.interaction_token
        )

    async def fetch_initial_response(self):
        return await self.client.rest.fetch_initial_interaction_response(
            self.client.client_id, self.interaction_token
        )

    async def edit_interaction(
        self,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: "ActionRow" = None,
        files: List[Any] | None = None,
        payload_json: str | None = None,
        attachments: Any | None = None
    ):
        return await self.client.rest.edit_original_interaction_response(
            application_id=self.client.client_id,
            interaction_token=self.interaction_token,
            content=content,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            files=files,
            payload_json=payload_json,
            attachments=attachments
        )
