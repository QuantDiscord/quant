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
from enum import Enum

import attrs


class TextInputStyle(Enum):
    """Discord text input style

    Attributes
    ==========
    SHORT:
        Small text input
    PARAGRAPH:
        Big text input
    """
    NONE = 0
    SHORT = 1
    PARAGRAPH = 2


@attrs.define(kw_only=True, hash=True)
class TextInput:
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
    INTERACTION_TYPE = 4

    type: int = attrs.field(default=INTERACTION_TYPE)
    custom_id: str = attrs.field()
    style: TextInputStyle = attrs.field(default=TextInputStyle.SHORT)
    label: str = attrs.field()
    min_length: int = attrs.field(default=0)
    max_length: int = attrs.field(default=4000)
    required: bool = attrs.field(default=True)
    value: str = attrs.field(default=None)
    placeholder: str = attrs.field(default=None)
