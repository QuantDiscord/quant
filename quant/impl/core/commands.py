from quant.impl.core.context import MessageCommandContext


class Command:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    async def callback(self, context: MessageCommandContext, *args) -> None:
        pass


class MessageCommand(Command):
    ...
