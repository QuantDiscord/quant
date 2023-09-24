import asyncio
import inspect
from typing import Coroutine, Callable, Any, Dict

from dispy.impl.core.commands import MessageCommand
from dispy.impl.core.exceptions.command_exceptions import CommandNotFoundException, CommandArgumentsNotFound
from dispy.impl.core.gateway import Gateway
from dispy.data.intents import Intents
from dispy.impl.core.exceptions.library_exception import LibraryException
from dispy.impl.core.rest import DiscordREST
from dispy.impl.events.event import BaseEvent
from dispy.impl.events.guild.message_events.message_event import MessageCreateEvent
from dispy.data.model import BaseModel
from dispy.data.activities.activity import ActivityBuilder
from dispy.impl.core.context import MessageCommandContext


class Client:
    def __init__(
        self,
        token: str,
        intents: Intents,
        prefix: str = None,
        with_mobile_status: bool = False
    ) -> None:
        self.loop = asyncio.get_event_loop()
        self.token = token
        self.prefix = prefix
        self.intents = intents
        self.with_mobile_status = with_mobile_status
        self.gateway: Gateway = Gateway(
            token=token,
            intents=self.intents,
            mobile_status=self.with_mobile_status
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

    def add_listener(self, event, coro: _Coroutine) -> None:
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
                    context = MessageCommandContext(
                        client=self, message=event.message
                    )
                    await command.callback(context, *arguments)
                except TypeError as e:
                    raise CommandArgumentsNotFound(e)
