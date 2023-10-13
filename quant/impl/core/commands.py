from typing import Dict, Type

from quant.impl.core.context import MessageCommandContext


class Command:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    async def callback(self, context: MessageCommandContext, *args) -> None:
        pass

    callback_func = callback

    def set_callback(self, coro):
        self.callback_func = coro


class MessageCommand(Command):
    ...


class SlashCommand(Command):
    def __init__(self, custom_id: str, options: Dict[str, Type] | None = None, **kwargs) -> None:
        super().__init__(kwargs.get("name"), kwargs.get("description"))
        self.options = options
