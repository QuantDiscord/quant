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
import enum

import attrs

from .emoji import Emoji
from quant.entities.api.backend import CallbackBackend
from quant.impl.core.context import ButtonContext


class ButtonStyle(enum.Enum):
    """Discord button styles"""
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


@attrs.define
class Button(CallbackBackend[ButtonContext]):
    """Represents a discord button

    Parameters
    ==========
    custom_id: :class:`str | None`
        Button custom ID
    style: :class:`ButtonStyle`
        Discord button style, default PRIMARY
    label: :class:`str`
        Button label
    emoji: :class:`Emoji | None`
        Button emoji
    url: :class:`str | None`
        Button redirect url
    disabled: :class:`bool`
        Set/check is button disabled
    """
    BUTTON_COMPONENT_TYPE = 2
    INTERACTION_TYPE = 3

    custom_id: str = attrs.field()
    label: str | None = attrs.field(default=None)
    style: ButtonStyle = attrs.field(default=ButtonStyle.PRIMARY)
    emoji: Emoji | str | None = attrs.field(default=None)
    url: str | None = attrs.field(default=None)
    disabled: bool = attrs.field(default=False)


def button(
    custom_id: str,
    label: str | None = None,
    style: ButtonStyle | int = ButtonStyle.PRIMARY,
    emoji: Emoji | str | None = None,
    url: str | None = None,
    disabled: bool = False,
) -> Button:
    if isinstance(style, int):
        style = ButtonStyle(style)

    return Button(
        custom_id=custom_id,
        label=label,
        style=style,
        emoji=emoji,
        url=url,
        disabled=disabled
    )
