from typing import Any, List, TypeVar

import attrs

from quant.entities.permissions import Permissions
from quant.entities.interactions.slash_option import ApplicationCommandOption, SlashOptionType
from quant.impl.core.context import BaseContext, InteractionContext
from quant.entities.snowflake import Snowflake
from quant.entities.interactions.application_command import ApplicationCommandTypes

ContextT = TypeVar("ContextT", bound=BaseContext | InteractionContext)


class Command:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    async def callback(self, context: ContextT, *args) -> None:
        pass

    callback_func = callback

    def set_callback(self, coro):
        self.callback_func = coro


class ApplicationCommandObject(Command):
    def __init__(
        self,
        cmd_id: Snowflake,
        application_id: Snowflake,
        dm_permissions: bool = False,
        default_permission: bool = False,
        nsfw: bool = False,
        cmd_type: ApplicationCommandTypes = ApplicationCommandTypes.CHAT_INPUT,
        guild_id: Snowflake | None = None,
        options: List[ApplicationCommandOption] = None,
        default_member_permissions: Permissions | None = None,
        **kwargs
    ) -> None:
        super().__init__(kwargs.get("name"), kwargs.get("description"))
        if default_member_permissions is not None:
            self.default_member_permissions = default_member_permissions.value

        self.options = options
        self.guild_id = guild_id
        self.nsfw = nsfw
        self.default_permission = default_permission
        self.dm_permissions = dm_permissions
        self.type = cmd_type
        self.id = cmd_id
        self.application_id = application_id

    @property
    def mention(self) -> str:
        return f"</{self.name}:{self.id}>"

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
            option_type=option_type
        )
        self.options.append(option)
        return option


class SlashCommand(ApplicationCommandObject):
    def __init__(
        self,
        options: List[ApplicationCommandOption] = None,
        guild_ids: List[Snowflake | int] | None = None,
        **kwargs
    ) -> None:
        super().__init__(kwargs.get("name"), kwargs.get("description"), **kwargs)

        self.options = options
        self.guild_ids = guild_ids
