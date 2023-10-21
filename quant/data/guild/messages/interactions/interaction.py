from typing import Any, List

import attrs

from quant.data.user import User
from quant.data.guild.messages.interactions.modals.modal import Modal
from quant.data.guild.messages.embeds import Embed
from quant.data.guild.messages.mentions.allowed_mentions import AllowedMentions
from quant.data.guild.messages.message_flags import MessageFlags
from quant.data.guild.guild_object import Guild
from quant.data.guild.members.member import GuildMember
from quant.data.guild.messages.interactions.interaction_data import InteractionData
from quant.data.guild.messages.interactions.interaction_type import InteractionType
from quant.data.guild.messages.interactions.response.modal_response import ModalInteractionCallbackData
from quant.data.gateway.snowflake import Snowflake
from quant.data.guild.messages.interactions.response.interaction_callback_data import InteractionCallbackData
from quant.data.guild.messages.interactions.response.interaction_callback_type import InteractionCallbackType
from quant.data.model import BaseModel
from quant.utils.attrs_extensions import execute_converters, int_converter


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Interaction(BaseModel):
    interaction_name: str = attrs.field(alias="name", default=None)
    interaction_id: Snowflake = attrs.field(alias="id", default=0, converter=int_converter)
    application_id: Snowflake = attrs.field(default=0, converter=int_converter)
    interaction_type: InteractionType = attrs.field(
        alias="type",
        default=InteractionType.PING,
        converter=InteractionType
    )
    interaction_data: InteractionData = attrs.field(alias="data", default=None, converter=InteractionData.as_dict)
    guild: Guild = attrs.field(default=None, converter=Guild.as_dict)
    guild_id: Snowflake = attrs.field(default=0, converter=int_converter)
    channel: Any = attrs.field(default=None)
    channel_id: Snowflake = attrs.field(default=0, converter=int_converter)
    member: GuildMember | None = attrs.field(default=None, converter=GuildMember.as_dict)
    user: User | None = attrs.field(default=None, converter=User.as_dict)
    interaction_token: str = attrs.field(default=None, alias="token")
    version: int = attrs.field(default=-1, converter=int_converter)
    app_permissions: str = attrs.field(default=None)
    locale: str = attrs.field(default=None)
    guild_locale: str = attrs.field(default=None)
    entitlements: List[Any] = attrs.field(default=None)
    entitlement_sku_ids: Any = attrs.field(default=None)

    async def respond(
        self,
        content: str | None = None,
        tts: bool = False,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        flags: MessageFlags | int = 0,
        components: List[Any] = None,  # TODO: Fix circular import when Component class here
        attachments: List[Any] = None
    ) -> None:
        if components is not None:
            components = [component.as_json() for component in components]

        if embed is not None:
            embeds = [embed]

        await self.client.rest.create_interaction_response(
            InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
            InteractionCallbackData(
                content=content,
                tts=tts,
                embeds=embeds,
                allowed_mentions=allowed_mentions,
                flags=flags if flags <= 0 else flags.value,
                components=components,
                attachments=attachments
            ), self.interaction_id, self.interaction_token
        )

    async def respond_modal(self, modal: Modal):
        await self.client.rest.create_interaction_response(
            InteractionCallbackType.MODAL,
            ModalInteractionCallbackData(
                custom_id=modal.custom_id,
                title=modal.title,
                components=[component.as_json() for component in modal.components]
            ),
            self.interaction_id, self.interaction_token
        )

    async def fetch_initial_response(self):
        return await self.client.rest.fetch_initial_interaction_response(
            self.client.client_id, self.interaction_token
        )
