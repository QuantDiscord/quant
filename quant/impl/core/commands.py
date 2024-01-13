from typing import Dict, Any, List

from quant.entities.interactions.slash_option import SlashOption
from quant.impl.core.context import MessageCommandContext
from quant.entities.snowflake import Snowflake


class Command:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    async def callback(self, context: MessageCommandContext, *args) -> None:
        pass

    callback_func = callback

    def set_callback(self, coro):
        self.callback_func = coro


class SlashCommand(Command):
    def __init__(self, options: List[SlashOption] = None, guild_ids: List[Snowflake | int] | None = None, **kwargs) -> None:
        super().__init__(kwargs.get("name"), kwargs.get("description"))
        self.options = options
        self.guild_ids = guild_ids
