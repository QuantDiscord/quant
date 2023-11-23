import enum
from typing import List, Any, Dict
from typing_extensions import Self


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


class SlashOption:
    def __init__(
        self,
        name: str,
        description: str,
        min_value: int = None,
        max_value: int = None,
        min_length: int = None,
        max_length: int = None,
        autocomplete: bool = False,
        channel_types: List[Any] = None,
        options: List[Self] = None,
        choices: List[Any] = None,
        required: bool = False,
        option_type: SlashOptionType = SlashOptionType.STRING,
    ) -> None:
        self.name = name
        self.description = description
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length
        self.autocomplete = autocomplete
        self.channel_types = channel_types
        self.options = options
        self.choices = choices
        self.required = required
        self.option_type = option_type

    def as_json(self) -> Dict:
        payload = {
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
        }

        if self.options is not None:
            payload.update({"options": [option.as_json() for option in self.options]})

        return payload
