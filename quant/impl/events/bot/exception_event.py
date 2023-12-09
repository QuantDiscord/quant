from quant.impl.core.exceptions.library_exception import DiscordException
from quant.impl.events.event import InternalEvent


class QuantExceptionEvent(InternalEvent):
    exception: Exception

    def process_event(self, _, **kwargs):
        self.exception = DiscordException(kwargs)
        return self
