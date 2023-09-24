from __future__ import annotations

import datetime


import asyncio
from typing import List, Any, TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from dispy.data.guild.messages.emoji import Emoji

from dispy.data.user import User
from dispy.data.guild.members.member import GuildMember
from dispy.data.model import BaseModel
from dispy.data.guild.messages.embeds import Embed
from dispy.utils.attrs_extensions import execute_converters
from dispy.data.gateway.snowflake import Snowflake


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Message(BaseModel):
    type: int = attrs.field(default=None)
    timestamp: datetime.datetime = attrs.field(default=None)
    channel_id: Snowflake | None = attrs.field(default=None)
    position: Snowflake | None = attrs.field(default=None)
    message_id: int | None = attrs.field(alias="id", default=None)
    guild_id: Snowflake | None = attrs.field(default=None)
    author_as_member: GuildMember | None = attrs.field(alias="member", default=None, converter=GuildMember.from_dict)
    author_as_user: User | None = attrs.field(alias="author", default=None, converter=User.from_dict)
    content: str | None = attrs.field(default=None)
    nonce: str | int | None = attrs.field(default=None)
    tts: bool | None = attrs.field(default=None)
    embeds: List[Embed] | None = attrs.field(default=None)
    edited_timestamp: str = attrs.field(default=None)
    mention_everyone: bool | None = attrs.field(default=None)
    mentions: List[User] | None = attrs.field(default=None, converter=User.from_dict_iter)
    mention_roles: List[Any] | None = attrs.field(default=None)
    mention_channels: List[Any] | None = attrs.field(default=None)
    message_reference: Any | None = attrs.field(default=None)
    components: Any | None = attrs.field(default=None)
    stickers: List[Any] | None = attrs.field(default=None)
    attachments: List[Any] | None = attrs.field(default=None)
    flags: int | None = attrs.field(default=None)
    referenced_message: Message | None = attrs.field(default=None)
    pinned: bool = attrs.field(default=False)
    webhook_id: Snowflake | None = attrs.field(default=None)
    activity: Any | None = attrs.field(default=None)
    application: Any | None = attrs.field(default=None)
    application_id: Snowflake | None = attrs.field(default=None)
    interaction: Any | None = attrs.field(default=None)
    thread: Any | None = attrs.field(default=None)
    sticker_items: List[Any] | None = attrs.field(default=None)
    role_subscription_data: Any | None = attrs.field(default=None)

    async def delete(self, *, reason: str = None, delete_after: int = 0) -> None:
        await asyncio.sleep(delete_after)
        await self.client.rest.delete_message(self.channel_id, self.message_id, reason)

    async def create_reaction(self, emoji: Emoji) -> None:
        await self.client.rest.create_reaction(emoji, self.guild_id, self.channel_id, self.message_id)
