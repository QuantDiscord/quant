from typing_extensions import Self

from quant.impl.core.context import InteractionContext, MessageCommandContext, ModalContext
from quant.impl.core.exceptions.library_exception import DiscordException
from quant.impl.events.event import InternalEvent

ContextType = InteractionContext | MessageCommandContext | ModalContext


class QuantExceptionEvent(InternalEvent):
    exception: Exception
    context: ContextType

    def process_event(self, _, **kwargs):
        self.exception = DiscordException(kwargs)
        return self

    def build(self, context: ContextType, exception: Exception) -> Self:
        self.exception = DiscordException(exception)
        self.context = context
        return self
