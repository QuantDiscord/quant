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

from enum import Enum
from datetime import datetime
from typing import Any, List, TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from .user import User
    from .message import MessageReference, Attachment, MessageFlags, Message
    from .action_row import ActionRow

from .emoji import Reaction
from .model import BaseModel
from .snowflake import Snowflake
from .embeds import Embed
from .allowed_mentions import AllowedMentions
from .permissions import Permissions


class ChannelType(int, Enum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15
    GUILD_MEDIA = 16


@attrs.define(kw_only=True)
class Channel(BaseModel):
    id: Snowflake = attrs.field(default=0)
    type: ChannelType = attrs.field(default=0)
    guild_id: Snowflake = attrs.field(default=0)
    position: int = attrs.field(default=0)
    permission_overwrites: Any = attrs.field(default=None)
    name: str = attrs.field(default=None)
    topic: str = attrs.field(default=None)
    nsfw: bool = attrs.field(default=False)
    version: str = attrs.field(default=None, repr=False)
    status: str = attrs.field(default=None, repr=False)
    theme_color: str = attrs.field(default=None, repr=False)
    icon_emoji: str = attrs.field(default=None, repr=False)
    template: str = attrs.field(default=None, repr=False)
    icon: str = attrs.field(default=None)
    owner_id: Snowflake = attrs.field(default=0)
    application_id: Snowflake = attrs.field(default=0)
    managed: bool = attrs.field(default=False)
    parent_id: Snowflake = attrs.field(default=0)
    member_count: int = attrs.field(default=0)
    member: Any = attrs.field(default=None)
    default_auto_archive_duration: int = attrs.field(default=0)
    permissions: Permissions = attrs.field(default=None)
    flags: int = attrs.field(default=0)
    # Is forum
    # default_reaction_emoji: List[Reaction] = attrs.field(default=None)
    default_thread_rate_limit_per_user: int = attrs.field(default=0)
    default_sort_order: int = attrs.field(default=0)

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"

    async def send_message(
        self,
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
        attachments: List[Attachment] = None,
        flags: MessageFlags | int | None = None
    ) -> Message:
        return await self.client.rest.create_message(
            channel_id=self.id,
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


@attrs.define(kw_only=True)
class ThreadMetadata:
    archived: bool = attrs.field()
    auto_archive_duration: int = attrs.field()
    archive_timestamp: datetime = attrs.field()
    locked: bool = attrs.field()
    invitable: bool = attrs.field(default=False)
    create_timestamp: datetime = attrs.field()


@attrs.define(kw_only=True)
class VoiceChannel(Channel):
    bitrate: int = attrs.field(default=0)
    user_limit: int = attrs.field(default=0)
    rtc_region: str = attrs.field(default=None)
    video_quality_mode: int = attrs.field(default=0)


@attrs.define(kw_only=True)
class TextChannel(Channel):
    last_message_id: Snowflake = attrs.field(default=0)
    rate_limit_per_user: int = attrs.field(default=0)
    last_pin_timestamp: datetime = attrs.field(default=None)


@attrs.define(kw_only=True)
class Thread(TextChannel):
    total_message_sent: int = attrs.field()
    message_count: int = attrs.field()
    available_tags: List[Any] = attrs.field()
    applied_tags: List[Snowflake] = attrs.field()
    thread_metadata: ThreadMetadata = attrs.field()
    default_auto_archive_duration: datetime = attrs.field()
    member_count: int = attrs.field()
    recipients: List[User] = attrs.field(default=None)
