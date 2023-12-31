import enum
from typing import List, Any, Dict
from typing_extensions import Self

import attrs

from quant.utils.json_builder import MutableJsonBuilder


class SlashOptionType(enum.Enum):
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
class SlashOption:
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

    def as_json(self) -> Dict:
        payload = MutableJsonBuilder({
            'name': self.name.lower(),
            'description': self.description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'autocomplete': self.autocomplete,
            'channel_types': self.channel_types,
            'choices': self.choices,
            'required': self.required,
            'type': self.option_type.value
        })

        if self.options is not None:
            payload.put("options", [option.as_json() for option in self.options])

        return payload.asdict()
