"""
MIT License

Copyright (c) 2024 MagM1go

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
from __future__ import annotations as _

from typing import Any, List, TypeVar, Dict

import attrs

from quant.entities.api.backend import CallbackBackend
from quant.entities.integration import IntegrationTypes
from quant.entities.interactions.application_command import ApplicationCommandTypes, ApplicationCommandContexts
from quant.entities.interactions.slash_option import ApplicationCommandOption, SlashOptionType
from quant.entities.permissions import Permissions
from quant.entities.snowflake import Snowflake
from quant.entities.locales import DiscordLocale
from quant.impl.core.context import BaseContext, InteractionContext

ContextT = TypeVar("ContextT", bound=BaseContext | InteractionContext)


@attrs.define
class _Command(CallbackBackend[ContextT]):
    name: str = attrs.field()
    description: str = attrs.field(default="Empty description")


@attrs.define
class ApplicationCommandObject(_Command):
    name_localizations: Dict[DiscordLocale, str] = attrs.field(default=None)
    description_localizations: Dict[DiscordLocale, str] = attrs.field(default=None)
    cmd_id: Snowflake = attrs.field(default=Snowflake())
    application_id: Snowflake = attrs.field(default=Snowflake())
    dm_permissions: bool = attrs.field(default=False)
    default_permission: bool = attrs.field(default=False)
    nsfw: bool = attrs.field(default=False)
    cmd_type: ApplicationCommandTypes = attrs.field(default=ApplicationCommandTypes.CHAT_INPUT)
    guild_id: Snowflake = attrs.field(default=None),
    options: List[ApplicationCommandOption] = attrs.field(default=None),
    default_member_permissions: Permissions = attrs.field(default=Permissions.NONE),
    integration_types: List[IntegrationTypes] | None = attrs.field(default=None)
    contexts: List[ApplicationCommandContexts] | None = attrs.field(default=None)

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
            options=options if options else [],
            choices=choices,
            required=required,
            type=option_type
        )

        if self.options is not None:
            self.options.append(option)
            return option

        self.options = [option]
        return option

    def __hash__(self) -> int:
        return hash(self.cmd_id)


@attrs.define(hash=True)
class SlashSubCommand(ApplicationCommandOption, CallbackBackend[ContextT]):
    type: SlashOptionType = attrs.field(default=SlashOptionType.SUB_COMMAND)


@attrs.define(hash=True)
class SlashSubGroup(ApplicationCommandOption):
    type: SlashOptionType = attrs.field(default=SlashOptionType.SUB_COMMAND_GROUP)


@attrs.define
class SlashCommand(ApplicationCommandObject):
    options: List[ApplicationCommandOption] | None = attrs.field(default=None)
    guild_ids: List[Snowflake | int] | None = attrs.field(default=None)

    def __hash__(self) -> int:
        return hash(self.cmd_id)
