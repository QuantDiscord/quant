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

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.entities.user import User
from quant.impl.events.event import DiscordEvent
from quant.entities.message import Message


@attrs.define(kw_only=True)
class MessageCreateEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.MESSAGE_CREATE)
    message: Message = attrs.field(default=None)

    def emit(self, **kwargs) -> Self:
        if kwargs is None:
            return

        self.message = Message(**kwargs)
        self.cache_manager.add_message(self.message)

        return self


@attrs.define(kw_only=True)
class MessageEditEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.MESSAGE_UPDATE)
    old_message: Message = attrs.field(default=None)
    new_message: Message = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        self.new_message = Message(**kwargs)
        message = self.cache_manager.get_message(int(kwargs.get("id")))

        if message is None:
            return

        self.old_message = message
        return self


@attrs.define(kw_only=True)
class MessageDeleteEvent(DiscordEvent):
    event_api_name: EventTypes = attrs.field(default=EventTypes.MESSAGE_DELETE)
    author: User = attrs.field(default=None)
    message: Message = attrs.field(default=None)

    def emit(self, *args, **kwargs) -> Self:
        message = self.cache_manager.get_message(int(kwargs.get("id")))
        if message is not None:
            self.message = message

        return self

    @classmethod
    def set_author(cls, user: User):
        cls.author = user
