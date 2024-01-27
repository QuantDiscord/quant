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
