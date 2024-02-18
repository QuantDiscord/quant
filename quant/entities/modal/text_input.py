from enum import Enum

import attrs

from quant.api.entities.component import Component


class TextInputStyle(Enum):
    """Discord text input style

    Attributes
    ==========
    SHORT:
        Small text input
    PARAGRAPH:
        Big text input
    """
    SHORT = 1
    PARAGRAPH = 2


@attrs.define(kw_only=True)
class TextInput(Component):
    """Represents a discord text input

    Parameters
    =========
    custom_id: :class:`str`
        Text input custom ID
    style: :class:`TextInputStyle`
        Text input style
    label: :class:`str`
        Text input label
    min_length: :class:`int`
        Minimal content length
    max_length: :class:`int`
        Maximal content length
    required: :class:`bool`
        Required field or no
    value: :class:`str`
        Text input value
    placeholder: :class:`str`
        Placeholder
    """
    custom_id: str = attrs.field()
    style: TextInputStyle = attrs.field(default=TextInputStyle.SHORT)
    label: str = attrs.field()
    min_length: int = attrs.field(default=0)
    max_length: int = attrs.field(default=4000)
    required: bool = attrs.field(default=True)
    value: str = attrs.field(default=None)
    placeholder: str = attrs.field(default=None)
    _type: int = attrs.field(default=4, repr=False, alias="type")

    def as_json(self):
        return {
            'type': self._type,
            'custom_id': self.custom_id,
            'style': self.style.value,
            'label': self.label,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'required': self.required,
            'value': self.value,
            'placeholder': self.placeholder
        }
