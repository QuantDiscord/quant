from __future__ import annotations as _

import enum
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

import attrs


class SlashOptionType(enum.Enum):
    NONE = 0
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


@attrs.define
class ApplicationCommandOption:
    name: str = attrs.field()
    description: str = attrs.field()
    min_value: int = attrs.field(default=None)
    max_value: int = attrs.field(default=None)
    min_length: int = attrs.field(default=None)
    max_length: int = attrs.field(default=None)
    autocomplete: bool = attrs.field(default=False)
    channel_types: List[Any] = attrs.field(default=None)
    options: List[Self] = attrs.field(default=None)
    choices: List[Any] = attrs.field(default=None)
    required: bool = attrs.field(default=False)
    option_type: SlashOptionType = attrs.field(default=SlashOptionType.STRING)
