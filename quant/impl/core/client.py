from __future__ import annotations

import asyncio
import base64
import inspect
from typing import (
    Coroutine,
    Callable,
    Any,
    Dict,
    overload,
    TypeVar,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from quant.entities.button import Button

from quant.entities.interactions.component_types import ComponentType
from quant.impl.core.shard import Shard
from quant.entities.interactions.interaction import Interaction
from quant.entities.snowflake import Snowflake
from quant.entities.user import User
from quant.impl.events.bot.exception_event import QuantExceptionEvent
from quant.impl.events.bot.ready_event import ReadyEvent
from quant.entities.interactions.interaction import InteractionType
from quant.entities.modal.modal import Modal
from quant.impl.core.commands import SlashCommand
from quant.impl.core.context import InteractionContext, ModalContext, ButtonContext
from quant.impl.events.bot.interaction_create_event import InteractionCreateEvent
from quant.impl.core.gateway import Gateway
from quant.entities.intents import Intents
from quant.impl.core.exceptions.library_exception import DiscordException
from quant.impl.core.rest import RESTImpl
from quant.impl.events.event import Event, InternalEvent, DiscordEvent
from quant.entities.model import BaseModel
from quant.entities.activity import ActivityData


class Client:
    T = TypeVar("T")

    def __init__(
        self,
        token: str,
        intents: Intents = Intents.ALL_UNPRIVILEGED,
        prefix: str = None,
        shard_id: int = 0,
        num_shards: int = 1
    ) -> None:
        self.my_user: User | None = None
        self.token = token
        self.prefix = prefix
        self.intents = intents
        self.gateway: Gateway = Gateway(
            token=token,
            intents=self.intents,
            shard_id=shard_id,
            num_shards=num_shards
        )
        self.loop = asyncio.get_event_loop()
        self.rest = RESTImpl(self.gateway.token)
        self.cache = self.gateway.cache
        self.client_id: int = self._decode_token_to_id()
        self.event_factory = self.gateway.event_factory
        self.event_controller = self.gateway.event_controller
        
        self._modals: Dict[str, Modal] = {}
        self._buttons: Dict[str, Button] = {}
        self._slash_commands: Dict[str, SlashCommand] = {}

        self.add_listener(InteractionCreateEvent, self._listen_interaction_create)
        self.add_listener(ReadyEvent, self._set_client_user_on_ready)

    _Coroutine = Callable[..., Coroutine[Any, Any, Any]]

    def _decode_token_to_id(self) -> int:
        first_token_part = self.token.split('.')[0]
        token = first_token_part[4:] \
            if first_token_part.startswith('Bot') \
            else first_token_part
        decoded_token = base64.b64decode(token + "==")
        return int(decoded_token.decode("utf8"))

    def run(self, loop: asyncio.AbstractEventLoop = None) -> None:
        BaseModel.set_client(self)

        if loop is not None:
            self.gateway.loop = loop

        asyncio.ensure_future(self.gateway.start(), loop=loop or self.gateway.loop)

        self.gateway.loop.run_forever()

    def run_with_shards(self, num_shards: int, loop: asyncio.AbstractEventLoop = None) -> None:
        BaseModel.set_client(self)

        if loop is not None:
            self.gateway.loop = loop

        for shard_id in range(num_shards):
            shard = Shard(num_shards=num_shards, shard_id=shard_id)
            print(shard)
            asyncio.ensure_future(shard.start(self.token), loop=self.gateway.loop)

        self.gateway.loop.run_forever()

    async def set_activity(self, activity: ActivityData) -> None:
        await self.gateway.send_presence(
            activity=activity.activity,
            status=activity.status,
            since=activity.since,
            afk=activity.afk
        )

    @overload
    def add_listener(self, event: T, coro: _Coroutine) -> None:
        ...

    @overload
    def add_listener(self, coro: _Coroutine) -> None:
        ...

    def add_listener(self, *args) -> None:
        if len(args) == 1:
            self._add_listener_from_coro(args[0])
        else:
            event, coro = args
            self._add_listener_from_event_and_coro(event, coro)

    def _add_listener_from_event_and_coro(self, event: T, coro: _Coroutine) -> None:
        if inspect.iscoroutine(coro):
            raise DiscordException("Callback function must be coroutine")

        if not issubclass(event, Event):
            raise DiscordException(f"Subclass of event {event} must be BaseEvent")

        self.gateway.event_factory.add_event(event, coro)

    def _add_listener_from_coro(self, coro: _Coroutine) -> None:
        if inspect.iscoroutine(coro):
            raise DiscordException("Callback function must be coroutine")

        annotations = inspect.getmembers(coro)[0]
        try:
            event_type: Event = list(annotations[1].values())[0]

            # idk why linter warning there
            if not issubclass(event_type, (InternalEvent, Event, DiscordEvent)):  # type: ignore
                raise DiscordException(f"{event_type.__name__} must be subclass of Event")

            self.gateway.event_factory.add_event(event_type, coro)
        except IndexError:
            raise DiscordException(f"You must provide which event you need {coro}")

    def add_slash_command(self, *commands: SlashCommand, app_id: Snowflake | int = None) -> None:
        for command in commands:
            if inspect.iscoroutine(command.callback):
                raise DiscordException("Callback function must be coroutine")

            if len(self.slash_commands) == 100:
                raise DiscordException("You can't create more than 100 slash commands.")

            self.slash_commands[command.name] = command

            guild_ids = command.guild_ids
            if len(guild_ids) > 0:
                for guild_id in guild_ids:
                    asyncio.ensure_future(self.rest.create_guild_application_command(
                        application_id=self.client_id if app_id is None else app_id,
                        name=command.name,
                        description=command.description,
                        options=command.options,
                        guild_id=guild_id
                    ), loop=self.gateway.loop)
                continue

            asyncio.ensure_future(self.rest.create_application_command(
                application_id=self.client_id if app_id is None else app_id,
                name=command.name,
                description=command.description,
                options=command.options,
            ), loop=self.gateway.loop)

    def add_modal(self, *modals: Modal) -> None:
        for modal in modals:
            if inspect.iscoroutine(modal.callback):
                raise DiscordException("Callback function must be coroutine")

            self.modals[str(modal.custom_id)] = modal

    def add_button(self, *buttons: Button) -> None:
        for button in buttons:
            if inspect.iscoroutine(button.callback):
                raise DiscordException("Callback function must be coroutine")

            self._buttons[str(button.custom_id)] = button

    @property
    def slash_commands(self) -> Dict[str, SlashCommand]:
        return self._slash_commands

    @property
    def modals(self) -> Dict[str, Modal]:
        return self._modals

    @property
    def buttons(self) -> Dict[str, Button]:
        return self._buttons

    async def handle_application_command(self, interaction: Interaction) -> None:
        interaction_type = interaction.type

        if not interaction_type == InteractionType.APPLICATION_COMMAND:
            return

        context = InteractionContext(self, interaction)
        command_name = interaction.data.name

        if command_name in self.slash_commands.keys():
            command = self.slash_commands[command_name]
            await command.callback_func(context)

    async def handle_modal_submit(self, interaction: Interaction) -> None:
        interaction_type = interaction.type

        if not interaction_type == InteractionType.MODAL_SUBMIT:
            return

        context = ModalContext(self, interaction)
        custom_id = interaction.data.custom_id

        if custom_id in self.modals.keys():
            modal = self.modals[custom_id]
            await modal.callback_func(context)

    async def handle_message_components(self, interaction: Interaction) -> None:
        interaction_type = interaction.type

        if not interaction_type == InteractionType.MESSAGE_COMPONENT:
            return

        component_type = interaction.data.component_type
        match component_type:
            case ComponentType.BUTTON:
                context = ButtonContext(self, interaction, None)
                custom_id = interaction.data.custom_id

                if custom_id in self.buttons.keys():
                    button = self.buttons[custom_id]
                    await button.callback_func(context)

    async def _listen_interaction_create(self, event: InteractionCreateEvent):
        interaction = event.interaction

        try:
            await self.handle_application_command(interaction)
            await self.handle_message_components(interaction)
            await self.handle_modal_submit(interaction)
        except Exception as e:
            await self.gateway.event_controller.dispatch(
                self.gateway.event_factory.build_from_class(
                    QuantExceptionEvent(), InteractionContext(self, interaction), e
                )
            )
            raise e

    async def _set_client_user_on_ready(self, _: ReadyEvent) -> None:
        self.my_user = self.cache.get_users()[0]
