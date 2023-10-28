import asyncio
import inspect
from base64 import b64decode
from typing import (
    Coroutine,
    Callable,
    Any,
    Dict,
    overload,
    TypeVar,
    List
)
import warnings

from quant.data.gateway.snowflake import Snowflake
from quant.data.user import User
from quant.impl.events.bot.ready_event import ReadyEvent
from quant.data.guild.messages.interactions.interaction_type import InteractionType
from quant.data.components.modals.modal import Modal
from quant.impl.core.commands import SlashCommand, CombineCommand
from quant.impl.core.context import InteractionContext, CombineContext
from quant.impl.events.bot.interaction_create_event import InteractionCreateEvent
from quant.impl.core import MessageCommand, MessageCommandContext
from quant.impl.core.exceptions.command_exceptions import CommandNotFoundException, CommandArgumentsNotFound
from quant.impl.core.gateway import Gateway
from quant.data.intents import Intents
from quant.impl.core.exceptions.library_exception import LibraryException, ExperimentalFutureWarning
from quant.impl.core.rest import DiscordREST
from quant.impl.events.event import BaseEvent
from quant.data.model import BaseModel
from quant.data.activities.activity import ActivityBuilder
from quant.impl.events.guild.message_events import MessageCreateEvent


class Client:
    T = TypeVar("T")

    def __init__(
        self,
        token: str,
        intents: Intents = Intents.ALL_UNPRIVILEGED,
        prefix: str = None,
        mobile_status: bool = False,
        shards: List[int] = None
    ) -> None:
        self.my_user: User | None = None
        self.token = token
        self.prefix = prefix
        self.intents = intents
        self.mobile_status = mobile_status
        self.gateway: Gateway = Gateway(
            token=token,
            intents=self.intents,
            mobile_status=self.mobile_status,
            shards=shards
        )
        self.rest = DiscordREST(self.gateway.token)
        self.cache = self.gateway.cache
        self.client_id: int = self._decode_token_to_id()

        self._commands: Dict[str, MessageCommand] = {}
        self._slash_commands: Dict[str, SlashCommand] = {}
        self._combined_commands: Dict[str, CombineCommand] = {}
        self._modals: Dict[str, Modal] = {}

        self.add_listener(MessageCreateEvent, self._handle_message_commands)
        self.add_listener(InteractionCreateEvent, self._handle_interactions)
        self.add_listener(ReadyEvent, self._set_client_user)

    _Coroutine = Callable[..., Coroutine[Any, Any, Any]]

    def _decode_token_to_id(self) -> int:
        first_token_part = self.token.split('.')[0]
        token = first_token_part[4:] \
            if first_token_part.startswith('Bot') \
            else first_token_part
        return int(b64decode(token).decode('utf8'))

    def run(self, loop: asyncio.AbstractEventLoop = None) -> None:
        BaseModel.set_client(self)

        if loop is not None:
            self.gateway.loop = loop

        self.gateway.loop.run_until_complete(self.gateway.connect_ws())

    async def set_activity(self, activity: ActivityBuilder) -> None:
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
            raise LibraryException("Callback function must be coroutine")

        if not issubclass(event, BaseEvent):
            raise LibraryException(f"Subclass of event {event} must be BaseEvent")

        self.gateway.add_event(event.API_EVENT_NAME, event, coro)

    def _add_listener_from_coro(self, coro: _Coroutine) -> None:
        if inspect.iscoroutine(coro):
            raise LibraryException("Callback function must be coroutine")

        annotations = inspect.getmembers(coro)[0]
        try:
            event_type: BaseEvent = list(annotations[1].values())[0]

            # idk why linter warning there
            if not issubclass(event_type, BaseEvent):  # type: ignore
                raise LibraryException(f"{event_type.__name__} must be subclass of BaseEvent")

            self.gateway.add_event(event_type.API_EVENT_NAME, event_type, coro)
        except IndexError:
            raise LibraryException(f"You need provide which event you need in function {coro}")

    async def add_combine_command(self, *commands: CombineCommand):
        warnings.warn(
            "Combine commands is experimental feature and can be removed in future",
            category=ExperimentalFutureWarning
        )
        for command in commands:
            if inspect.iscoroutine(command.callback):
                raise LibraryException("Callback function must be coroutine")

            self.combined_commands[command.name] = command

    def add_message_command(self, *commands: MessageCommand) -> None:
        for command in commands:
            if inspect.iscoroutine(command.callback):
                raise LibraryException("Callback function must be coroutine")

            self.message_commands[command.name] = command

    async def add_slash_command(self, *commands: SlashCommand, app_id: Snowflake | int = None) -> None:
        for command in commands:
            if inspect.iscoroutine(command.callback):
                raise LibraryException("Callback function must be coroutine")

            if len(self.slash_commands) == 100:
                raise LibraryException("You can't create more than 100 slash commands.")

            self.slash_commands[command.name] = command

            await self.rest.create_application_command(
                application_id=self.client_id if app_id is None else app_id,
                name=command.name,
                description=command.description,
                options=command.options
            )

    def add_modal(self, *modals: Modal) -> None:
        for modal in modals:
            if inspect.iscoroutine(modal):
                raise LibraryException("Callback function must be coroutine")

            self.modals[str(modal.custom_id)] = modal

    @property
    def message_commands(self) -> Dict[str, MessageCommand]:
        return self._commands

    @property
    def slash_commands(self) -> Dict[str, SlashCommand]:
        return self._slash_commands

    @property
    def modals(self) -> Dict[str, Modal]:
        return self._modals

    @property
    def combined_commands(self) -> Dict[str, CombineCommand]:
        return self._combined_commands

    async def _handle_interactions(self, event: InteractionCreateEvent):
        interaction_type = event.interaction.interaction_type
        context = InteractionContext(self, event.interaction)

        match interaction_type:
            case InteractionType.APPLICATION_COMMAND:
                slash_commands = self.slash_commands.values()
                combined_commands = self.combined_commands.values()
                for command in list(slash_commands) + list(combined_commands):
                    if isinstance(command, CombineCommand) and command.name == event.interaction.interaction_data.name:
                        await command.callback_func(CombineContext(self, None, event.interaction))
                    elif command.name == event.interaction.interaction_data.name:
                        await command.callback_func(context)
            case InteractionType.MODAL_SUBMIT:
                for modal in self.modals.values():
                    if modal.custom_id == event.interaction.interaction_data.custom_id:
                        await modal.callback_func(context)

    async def _handle_message_commands(self, event: MessageCreateEvent) -> None:
        content = event.message.content

        if content is None or self.prefix is None:
            return

        if content.startswith(self.prefix):
            substring_command = content[1:].split()[0]
            arguments = content[len(substring_command) + 1:].split()

            if substring_command not in self.message_commands.keys():
                raise CommandNotFoundException(f"command {substring_command} not found")

            message_commands = self.message_commands.values()
            combined_commands = self.combined_commands.values()
            for command in list(message_commands) + list(combined_commands):
                try:
                    if not command.name == substring_command:
                        continue

                    context = MessageCommandContext(client=self, message=event.message)
                    if isinstance(command, CombineCommand):
                        await command.callback_func(CombineContext(
                            client=self,
                            original_message=event.message,
                            interaction=None
                        ), *arguments)
                    else:
                        await command.callback_func(context, *arguments)
                except TypeError as e:  # stupid but ok
                    raise CommandArgumentsNotFound(e)

    async def _set_client_user(self, _: ReadyEvent) -> None:
        self.my_user = self.cache.get_users()[0]

    @staticmethod
    def create_new_loop() -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        return loop
