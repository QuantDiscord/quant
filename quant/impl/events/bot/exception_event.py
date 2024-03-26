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
from __future__ import annotations

import attrs

from quant.impl.core.context import InteractionContext, ModalContext
from quant.impl.core.exceptions.library_exception import DiscordException
from quant.impl.events.event import InternalEvent

ContextType = InteractionContext | ModalContext


@attrs.define(kw_only=True)
class QuantExceptionEvent(InternalEvent):
    exception: Exception = attrs.field(default=None)
    context: ContextType = attrs.field(default=None)

    def emit(self, *args, **kwargs):
        self.exception = DiscordException(kwargs)
        return self

    @staticmethod
    def build(event: QuantExceptionEvent, *args, **kwargs) -> QuantExceptionEvent:
        context, exception = args[0], args[1]
        event.exception = exception
        event.context = context
        return event
