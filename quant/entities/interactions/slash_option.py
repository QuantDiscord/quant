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
from __future__ import annotations as _

import enum
from typing import List, Any, TYPE_CHECKING

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


@attrs.define(hash=True)
class ApplicationCommandOption:
    name: str = attrs.field()
    description: str = attrs.field()
    min_value: int = attrs.field(default=None)
    max_value: int = attrs.field(default=None)
    min_length: int = attrs.field(default=None)
    max_length: int = attrs.field(default=None)
    autocomplete: bool = attrs.field(default=False)
    channel_types: List[Any] = attrs.field(default=None)
    options: List[ApplicationCommandOption] = attrs.field(default=None)
    choices: List[Any] = attrs.field(default=None)
    required: bool = attrs.field(default=False)
    type: SlashOptionType = attrs.field(default=SlashOptionType.STRING)
