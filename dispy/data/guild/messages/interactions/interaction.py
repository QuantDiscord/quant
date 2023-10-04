from typing import Any, List

import attrs

from dispy.data.user import User
from dispy.data.guild.messages.message import Message
from dispy.data.guild.messages.embeds import Embed
from dispy.data.guild.messages.mentions.allowed_mentions import AllowedMentions
from dispy.data.guild.messages.message_flags import MessageFlags
from dispy.data.guild.guild_object import Guild
from dispy.data.guild.members.member import GuildMember
from dispy.data.guild.messages.interactions.interaction_data import InteractionData
from dispy.data.guild.messages.interactions.interaction_type import InteractionType
from dispy.data.gateway.snowflake import Snowflake
from dispy.data.guild.messages.interactions.response.interaction_callback_data import InteractionCallbackData
from dispy.data.guild.messages.interactions.response.interaction_callback_type import InteractionCallbackType
from dispy.data.model import BaseModel
from dispy.utils.attrs_extensions import execute_converters, snowflake_to_int


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Interaction(BaseModel):
    interaction_id: Snowflake = attrs.field(alias="id", default=0, converter=snowflake_to_int)
    application_id: Snowflake = attrs.field(default=0, converter=snowflake_to_int)
    interaction_type: InteractionType = attrs.field(alias="type", default=InteractionType.PING)
    interaction_data: InteractionData = attrs.field(alias="data", default=None)
    guild: Guild = attrs.field(default=None)
    guild_id: Snowflake = attrs.field(default=0, converter=snowflake_to_int)
    channel: Any = attrs.field(default=None)
    channel_id: Snowflake = attrs.field(default=0, converter=snowflake_to_int)
    member: GuildMember | None = attrs.field(default=None, converter=GuildMember.as_dict)
    user: User | None = attrs.field(default=None, converter=User.as_dict)
    interaction_token: str = attrs.field(default=None, alias="token")
    version: int = attrs.field(default=-1, converter=int)
    message: Message = attrs.field(default=None, converter=Message.as_dict)
    app_permissions: str = attrs.field(default=None)
    locale: str = attrs.field(default=None)
    guild_locale: str = attrs.field(default=None)
    entitlements: List[Any] = attrs.field(default=None)
    entitlement_sku_ids: Any = attrs.field(default=None)

    async def respond(
        self,
        content: str | None = None,
        tts: bool = False,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        flags: MessageFlags = 0,
        components: List[Any] = None,
        attachments: List[Any] = None
    ) -> None:
        await self.client.rest.create_interaction_response(
            InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
            InteractionCallbackData(
                content=content,
                tts=tts,
                embeds=embeds,
                allowed_mentions=allowed_mentions,
                flags=flags.value,
                components=components,
                attachments=attachments
            ), self.interaction_id, self.interaction_token
        )
