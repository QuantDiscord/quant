from __future__ import annotations as _

import enum
from typing import List, Any, Dict

import attrs

from quant.entities.snowflake import Snowflake
from quant.entities.user import User
from quant.entities.roles import GuildRole
from quant.entities.member import GuildMember
from quant.entities.channel import Channel
from quant.entities.message import Message, Attachment
from quant.entities.guild import Guild
from quant.entities.permissions import Permissions
from quant.entities.locales import DiscordLocale
from quant.entities.integration import IntegrationTypes


class InteractionType(int, enum.Enum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class ApplicationCommandType(int, enum.Enum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


class ApplicationCommandOptionType(int, enum.Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11


@attrs.define(kw_only=True)
class InteractionResolvedData:
    users: List[User] = attrs.field()
    members: List[GuildMember] = attrs.field()
    roles: List[GuildRole] = attrs.field()
    channels: List[Channel] = attrs.field()
    messages: List[Message] = attrs.field()
    attachments: List[Attachment] = attrs.field()


@attrs.define(kw_only=True)
class ApplicationCommandInteractionDataOption:
    name: str = attrs.field()
    type: ApplicationCommandOptionType = attrs.field()
    value: str | int | bool | float = attrs.field()
    options: List[ApplicationCommandInteractionDataOption] = attrs.field()
    focused: bool = attrs.field()


@attrs.define(kw_only=True)
class InteractionData:
    id: Snowflake = attrs.field()
    name: str = attrs.field()
    type: ApplicationCommandType = attrs.field()
    resolved: InteractionResolvedData | None = attrs.field()
    options: List[ApplicationCommandInteractionDataOption] = attrs.field()
    guild_id: Snowflake | None = attrs.field()
    target_id: Snowflake | None = attrs.field()


@attrs.define(kw_only=True)
class PartialInteraction:
    id: Snowflake = attrs.field()
    application_id: Snowflake = attrs.field()
    type: InteractionType = attrs.field()
    token: str = attrs.field()
    version: int = attrs.field()
    authorizing_integration_owners: Dict[Any, Any] = attrs.field()
    """Not supported yet"""
    context: IntegrationTypes | None = attrs.field()


@attrs.define(kw_only=True)
class CommandInteraction(PartialInteraction):
    data: InteractionData | None = attrs.field()
    guild: Guild | None = attrs.field()
    guild_id: Snowflake | None = attrs.field()
    channel: Channel | None = attrs.field()
    channel_id: Snowflake | None = attrs.field()
    member: GuildMember | None = attrs.field()
    user: User | None = attrs.field()
    message: Message | None = attrs.field()
    app_permissions: Permissions = attrs.field()
    locale: DiscordLocale | None = attrs.field()
    guild_locale: DiscordLocale | None = attrs.field()
    entitlements: Any = attrs.field()
    """Not supported yet"""
