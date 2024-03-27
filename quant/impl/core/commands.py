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
from typing import Any, List, TypeVar

import attrs

from quant.entities.api.backend import CallbackBackend
from quant.entities.permissions import Permissions
from quant.entities.interactions.slash_option import ApplicationCommandOption, SlashOptionType
from quant.impl.core.context import BaseContext, InteractionContext
from quant.entities.snowflake import Snowflake
from quant.entities.interactions.application_command import ApplicationCommandTypes

ContextT = TypeVar("ContextT", bound=BaseContext | InteractionContext)


@attrs.define
class Command(CallbackBackend[ContextT]):
    name: str = attrs.field()
    description: str = attrs.field()


@attrs.define
class ApplicationCommandObject(Command):
    cmd_id: Snowflake = attrs.field(default=Snowflake(0))
    application_id: Snowflake = attrs.field(default=Snowflake(0))
    dm_permissions: bool = attrs.field(default=False)
    default_permission: bool = attrs.field(default=False)
    nsfw: bool = attrs.field(default=False)
    cmd_type: ApplicationCommandTypes = attrs.field(default=ApplicationCommandTypes.CHAT_INPUT)
    guild_id: Snowflake | None = attrs.field(default=None),
    options: List[ApplicationCommandOption] = attrs.field(default=None),
    default_member_permissions: Permissions | None = attrs.field(default=None),

    @property
    def mention(self) -> str:
        return f"</{self.name}:{self.cmd_id}>"

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
        options: List[ApplicationCommandOption] | None = None,
        choices: List[Any] | None = None,
        required: bool = False,
        option_type: SlashOptionType | None = None
    ) -> ApplicationCommandOption:
        option = ApplicationCommandOption(
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
            type=option_type
        )

        if self.options is not None:
            self.options.append(option)
            return option

        self.options = [option]
        return option


@attrs.define
class SlashCommand(ApplicationCommandObject):
    options: List[ApplicationCommandOption] | None = attrs.field(default=None)
    guild_ids: List[Snowflake | int] | None = attrs.field(default=None)
