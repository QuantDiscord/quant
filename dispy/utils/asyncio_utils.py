import asyncio
import warnings
from asyncio import AbstractEventLoop
from contextlib import suppress


# https://github.com/hikari-py/hikari/blob/4eda2eef15681143ca7957f6f5cec1df1461fd39/hikari/internal/aio.py#L195
def get_loop() -> AbstractEventLoop:
    with suppress(RuntimeError):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            loop = asyncio.get_event_loop_policy().get_event_loop()

        if not loop.is_closed():
            return loop

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop
