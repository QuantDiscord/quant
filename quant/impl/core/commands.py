from typing import Dict, Any, List

from quant.entities.interactions.slash_option import SlashOption, SlashOptionType
from quant.impl.core.context import BaseContext
from quant.entities.snowflake import Snowflake


class Command:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    async def callback(self, context: BaseContext, *args) -> None:
        pass

    callback_func = callback

    def set_callback(self, coro):
        self.callback_func = coro


class SlashCommand(Command):
    def __init__(
        self,
        options: List[SlashOption] = None,
        guild_ids: List[Snowflake | int] | None = None,
        **kwargs
    ) -> None:
        super().__init__(kwargs.get("name"), kwargs.get("description"))
        if options is None:
            self.options = []

        self.guild_ids = guild_ids

    def option(
        self,
        name: str,
        description: str,
        min_value: int | None = None,
        max_value: int | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        autocomplete: bool = False,
        channel_types: List[Any] | None = None,
        options: List[SlashOption] | None = None,
        choices: List[Any] | None = None,
        required: bool = False,
        option_type: SlashOptionType | None = None
    ) -> SlashOption:
        option = SlashOption(
            name=name,
            description=description,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            autocomplete=autocomplete,
            channel_types=channel_types,
            options=options,
            choices=choices,
            required=required,
            option_type=option_type
        )
        self.options.append(option)
        return option
