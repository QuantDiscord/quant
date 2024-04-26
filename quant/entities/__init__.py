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
from .action_row import ActionRow
from .activity import (
    Activity,
    ActivityBuilder,
    ActivityFlags,
    ActivityType,
    ActivityStatus,
    ActivityAssets,
    ActivityData
)
from .allowed_mentions import AllowedMentions, AllowedMentionsTypes, suppress_mentions
from .button import Button, ButtonStyle, button
from .channel import Channel, Thread, ThreadMetadata, ChannelType, VoiceChannel
from .embeds import *
from .emoji import Emoji, Reaction, PartialReaction, PartialEmoji
from .guild import Guild
from .invite import Invite
from .intents import Intents
from .member import GuildMember
from .roles import GuildRole
from .message_flags import MessageFlags
from .snowflake import Snowflake
from .user import User
from .voice_server_update import VoiceServer
from .voice_state_update import VoiceState
from .webhook import Webhook, WebhookTypes
from .modal import Modal, ModalInteractionCallbackData, TextInput, TextInputStyle
from .interactions import (
    Interaction,
    InteractionData,
    InteractionType,
    InteractionResponse,
    InteractionCallbackType,
    InteractionCallbackData,
    InteractionDataOption,
    ApplicationCommandOptionType,
    ApplicationCommandOption,
    SlashOptionType,
    ApplicationCommandContexts
)
from .integration import IntegrationTypes, Integration
from .permissions import Permissions
from .message import Message, MessageReference, Attachment
from .color import Color, RGB, Hex
from .poll import Poll, PollResults, PollAnswer, PollMedia, PollMediaType, poll, Answer
from .locales import DiscordLocale


__all__ = (
    "Attachment",
    "ActionRow",
    "Activity",
    "ActivityFlags",
    "ActivityBuilder",
    "ActivityType",
    "ActivityAssets",
    "ActivityStatus",
    "ActivityData",
    "AllowedMentions",
    "AllowedMentionsTypes",
    "Button",
    "ButtonStyle",
    "Channel",
    "Message",
    "MessageReference",
    "Embed",
    "EmbedThumbnail",
    "EmbedImage",
    "EmbedField",
    "EmbedAuthor",
    "EmbedFooter",
    "Emoji",
    "Reaction",
    "PartialReaction",
    "Guild",
    "GuildMember",
    "MessageFlags",
    "Snowflake",
    "User",
    "VoiceState",
    "VoiceServer",
    "Webhook",
    "WebhookTypes",
    "Intents",
    "ApplicationCommandOptionType",
    "InteractionDataOption",
    "Interaction",
    "InteractionCallbackData",
    "InteractionCallbackType",
    "InteractionType",
    "InteractionResponse",
    "InteractionData",
    "ApplicationCommandOption",
    "SlashOptionType",
    "Modal",
    "ModalInteractionCallbackData",
    "TextInput",
    "TextInputStyle",
    "Invite",
    "Thread",
    "ThreadMetadata",
    "ChannelType",
    "VoiceChannel",
    "embed",
    "button",
    "Permissions",
    "GuildRole",
    "Integration",
    "IntegrationTypes",
    "ApplicationCommandContexts",
    "suppress_mentions",
    "Color",
    "RGB",
    "Hex",
    "PollMedia",
    "Poll",
    "PollMediaType",
    "PollResults",
    "poll",
    "Answer",
    "PartialEmoji",
    "DiscordLocale"
)
