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
    """
    Represents a discord message.

    Parameters
    ----------
    type: int
        Message type.
    timestamp: datetime
        Timestamp of the message.
    channel_id: Snowflake | None
        ID of the channel where the message was sent.
    position: Snowflake | None
        Position of the message in the channel.
    id: int | None
        Unique ID of the message.
    guild_id: Snowflake | None
        ID of the guild where the message was sent.
    member: GuildMember | None
        Member who sent the message.
    author: User | None
        User who sent the message.
    content: str | None
        Content of the message.
    nonce: str | int | None
        Nonce of the message.
    tts: bool | None
        Whether the message is text-to-speech.
    embeds: List[Embed] | None
        List of embedded content in the message.
    edited_timestamp: str
        Timestamp when the message was edited.
    mention_everyone: bool | None
        Whether the message mentions everyone.
    mentions: List[User] | None
        List of users mentioned in the message.
    mention_roles: List[Any] | None
        List of roles mentioned in the message.
    mention_channels: List[Any] | None
        List of channels mentioned in the message.
    message_reference: Any | None
        Reference to another message.
    components: ActionRow | None
        Action row components in the message.
    stickers: List[Any] | None
        List of stickers in the message.
    attachments: List[Attachment] | None
        List of attachments in the message.
    flags: int | None
        Message flags.
    referenced_message: Self | None
        Reference to another message.
    pinned: bool
        Whether the message is pinned.
    webhook_id: Snowflake | None
        ID of the webhook that sent the message.
    activity: Any | None
        Activity associated with the message.
    application: Any | None
        Application associated with the message.
    application_id: Snowflake | None
        ID of the application associated with the message.
    interaction: Interaction
        Interaction associated with the message.
    thread: Thread | None
        Thread associated with the message.
    sticker_items: List[Any] | None
        List of sticker items in the message.
    role_subscription_data: Any | None
        Role subscription data associated with the message.
    resolved: bool | None
        Whether the message is resolved.
    """
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
        """|coroutine_link|
        Reply the message
        """
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
