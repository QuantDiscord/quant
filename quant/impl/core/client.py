import asyncio
import inspect
from typing import (
    Coroutine,
    Callable,
    Any,
    List,
    Dict,
    overload,
    TypeVar
)

from quant.impl.core import MessageCommand, MessageCommandContext
from quant.impl.core.exceptions.command_exceptions import CommandNotFoundException, CommandArgumentsNotFound
from quant.impl.core.gateway import Gateway
from quant.data.intents import Intents
from quant.impl.core.exceptions.library_exception import LibraryException
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
        intents: Intents,
        prefix: str = None,
        mobile_status: bool = False
    ) -> None:
        self.loop = asyncio.get_event_loop()
        self.token = token
        self.prefix = prefix
        self.intents = intents
        self.mobile_status = mobile_status
        self.gateway: Gateway = Gateway(
            token=token,
            intents=self.intents,
            mobile_status=self.mobile_status
        )
        self.rest = DiscordREST(self.gateway.token)
        self.cache = self.gateway.cache

        self._commands: Dict[str, MessageCommand] = {}

        self.add_listener(MessageCreateEvent, self._on_message_execute_command)

    _Coroutine = Callable[..., Coroutine[Any, Any, Any]]

    def run(self) -> None:
        BaseModel.set_client(self)
        self.gateway.loop.run_until_complete(self.gateway.connect_ws())

    def set_activity(self, activity: ActivityBuilder) -> None:
        self.gateway.set_presence(
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
            coro = args[0]

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
        else:
            event, coro = args
            if inspect.iscoroutine(coro):
                raise LibraryException("Callback function must be coroutine")

            if not issubclass(event, BaseEvent):
                raise LibraryException(f"Subclass of event {event} must be BaseEvent")

            self.gateway.add_event(event.API_EVENT_NAME, event, coro)

    def add_message_command(self, command: MessageCommand) -> None:
        if inspect.iscoroutine(command.callback):
            raise LibraryException("Callback function must be coroutine")

        self.message_commands[command.name] = command

    @property
    def message_commands(self) -> Dict[str, MessageCommand]:
        return self._commands

    async def _on_message_execute_command(self, event: MessageCreateEvent) -> None:
        content = event.message.content

        if content is None or self.prefix is None:
            return

        if content.startswith(self.prefix):
            substring_command = content[1:].split()[0]
            arguments = content[len(substring_command) + 1:].split()

            if substring_command not in self.message_commands.keys():
                raise CommandNotFoundException(f"command {substring_command} not found")

            for command in self.message_commands.values():
                try:
                    context = MessageCommandContext(client=self, message=event.message)
                    await command.callback_func(context, *arguments)
                except TypeError as e:  # stupid but ok
                    raise CommandArgumentsNotFound(e)
