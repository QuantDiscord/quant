from __future__ import annotations

import asyncio
from typing import Any, List, TYPE_CHECKING

from datetime import datetime

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self
    from .interactions.interaction import Interaction

from .user import User
from .snowflake import Snowflake
from .channel import Thread
from .model import BaseModel
from .member import GuildMember
from .embeds import Embed
from .allowed_mentions import AllowedMentions
from .action_row import ActionRow
from .emoji import Emoji
from .message_flags import MessageFlags


@attrs.define(kw_only=True)
class Message(BaseModel):
    type: int = attrs.field(default=None)
    timestamp: datetime = attrs.field(default=None)
    channel_id: Snowflake | None = attrs.field(default=None)
    position: Snowflake | None = attrs.field(default=None)
    id: int | None = attrs.field(default=None)
    guild_id: Snowflake | None = attrs.field(default=None)
    member: GuildMember | None = attrs.field(default=None)
    author: User | None = attrs.field(default=None)
    content: str | None = attrs.field(default=None)
    nonce: str | int | None = attrs.field(default=None)
    tts: bool | None = attrs.field(default=None)
    embeds: List[Embed] | None = attrs.field(default=None)
    edited_timestamp: str = attrs.field(default=None)
    mention_everyone: bool | None = attrs.field(default=None)
    mentions: List[User] | None = attrs.field(default=None)
    mention_roles: List[Any] | None = attrs.field(default=None)
    mention_channels: List[Any] | None = attrs.field(default=None)
    message_reference: Any | None = attrs.field(default=None)
    components: ActionRow | None = attrs.field(default=None)
    stickers: List[Any] | None = attrs.field(default=None)
    attachments: List[Attachment] | None = attrs.field(default=None)
    flags: int | None = attrs.field(default=None)
    referenced_message: Self | None = attrs.field(default=None)
    pinned: bool = attrs.field(default=False)
    webhook_id: Snowflake | None = attrs.field(default=None)
    activity: Any | None = attrs.field(default=None)
    application: Any | None = attrs.field(default=None)
    application_id: Snowflake | None = attrs.field(default=None)
    interaction: Interaction = attrs.field(default=None)
    thread: Thread | None = attrs.field(default=None)
    sticker_items: List[Any] | None = attrs.field(default=None)
    role_subscription_data: Any | None = attrs.field(default=None)
    resolved: bool | None = attrs.field(default=None)

    async def reply(
        self,
        content: str | None = None,
        nonce: str | int | None = None,
        tts: bool = False,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        allowed_mentions: AllowedMentions | None = None,
        components: ActionRow | None = None,
        sticker_ids: List = None,
        files: List[Any] | None = None,
        payload_json: str | None = None,
        attachments: List[Attachment] | None = None,
        flags: int | None = None
    ) -> Self:
        return await self.client.rest.create_message(
            channel_id=self.channel_id,
            content=content,
            nonce=nonce,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            sticker_ids=sticker_ids,
            files=files,
            payload_json=payload_json,
            attachments=attachments,
            flags=flags,
            message_reference=MessageReference(
                message_id=self.id,
                channel_id=self.channel_id,
                guild_id=self.guild_id
            )
        )

    async def delete(self, *, reason: str = None, delete_after: int = 0) -> None:
        await asyncio.sleep(delete_after)
        await self.client.rest.delete_message(self.channel_id, self.id, reason)

    async def create_reaction(self, emoji: Emoji) -> None:
        await self.client.rest.create_reaction(emoji, self.guild_id, self.channel_id, self.id)

    async def edit_message(
        self,
        content: str = None,
        embed: Embed = None,
        embeds: List[Embed] = None,
        flags: MessageFlags = MessageFlags.NONE,
        allowed_mentions: AllowedMentions = None,
        components: ActionRow = None
    ) -> Self:
        return await self.client.rest.edit_message(
            channel_id=self.channel_id,
            message_id=self.id,
            content=content,
            embed=embed,
            embeds=embeds,
            flags=flags.value,
            allowed_mentions=allowed_mentions,
            components=components
        )

    async def remove_reactions(self) -> None:
        await self.client.rest.delete_all_reactions(channel_id=self.channel_id, message_id=self.id)

    async def remove_reactions_by_emoji(self, emoji: int | Snowflake | Emoji) -> None:
        await self.client.rest.delete_all_reactions_for_emoji(
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            message_id=self.id,
            emoji=emoji
        )


@attrs.define(kw_only=True)
class MessageReference:
    message_id: int | Snowflake = attrs.field(default=0)
    channel_id: int | Snowflake = attrs.field(default=0)
    guild_id: int | Snowflake = attrs.field(default=0)


@attrs.define(kw_only=True)
class Attachment:
    id: Snowflake | int = attrs.field(default=None)
    filename: str = attrs.field(default=None)
    description: str = attrs.field(default=None)
    content_type: str = attrs.field(default=None)
    size: int = attrs.field(default=None)
    url: str = attrs.field(default=None)
    proxy_url: str = attrs.field(default=None)
    height: int | None = attrs.field(default=None)
    width: int | None = attrs.field(default=None)
    ephemeral: bool = attrs.field(default=None)
    duration_secs: float | None = attrs.field(default=None)
    waveform: str | None = attrs.field(default=None)
    flags: int = attrs.field(default=None)
