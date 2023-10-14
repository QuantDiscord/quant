from __future__ import annotations

from typing import List, Any, Dict

from quant.data.guild.messages.interactions.slashes.slash_option_type import SlashOptionType


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
        options: List[SlashOption] = None,
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
        return {
            'name': self.name.lower(),
            'description': self.description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'autocomplete': self.autocomplete,
            'channel_types': self.channel_types,
            'options': self.options,
            'choices': self.choices,
            'required': self.required,
            'type': self.option_type.value
        }
