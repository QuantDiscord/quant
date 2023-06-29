from __future__ import annotations

import attrs
import asyncio
from typing import List, Any, Optional

from dispy.data.guild.members.member import GuildMember
from dispy.data.model import BaseModel
from dispy.data.gateway.snowflake import Snowflake
from dispy.data.user import User


@attrs.define(kw_only=True)
class Message(BaseModel):
    type: int = attrs.field(default=None)
    timestamp: int = attrs.field(default=None)
    channel_id: int | None = attrs.field(default=None, converter=Snowflake.object_id_from_snowflake)
    position: int | None = attrs.field(default=None)
    message_id: int | None = attrs.field(alias="id", default=None, converter=Snowflake.object_id_from_snowflake)
    guild_id: int | None = attrs.field(default=None, converter=Snowflake.object_id_from_snowflake)
    author_as_member: GuildMember | None = attrs.field(alias="member", default=None, converter=GuildMember.from_dict)
    author_as_user: User | None = attrs.field(alias="author", default=None, converter=User.from_dict)
    content: str | None = attrs.field(default=None)
    nonce: str | int | None = attrs.field(default=None)
    tts: bool | None = attrs.field(default=None)
    embeds: List[dict] | None = attrs.field(default=None)
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
    webhook_id: int | None = attrs.field(default=None, converter=Snowflake.object_id_from_snowflake)
    activity: Any | None = attrs.field(default=None)
    application: Any | None = attrs.field(default=None)
    application_id: int | None = attrs.field(default=None, converter=Snowflake.object_id_from_snowflake)
    interaction: Any | None = attrs.field(default=None)
    thread: Any | None = attrs.field(default=None)
    sticker_items: List[Any] | None = attrs.field(default=None)
    role_subscription_data: Any | None = attrs.field(default=None)

    async def delete(self, *, reason: str = None, delete_after: int = 0) -> None:
        await asyncio.sleep(delete_after)
        await self.client.rest.delete_message(self.channel_id, self.message_id, reason)
