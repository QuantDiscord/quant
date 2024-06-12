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

import asyncio
import base64
import inspect
from typing import (
    Coroutine,
    Callable,
    Any,
    List,
    Dict,
    overload,
    TypeVar,
    TYPE_CHECKING,
    get_type_hints,
    Type
)

if TYPE_CHECKING:
    from quant.impl.core.commands import ApplicationCommandObject
    from quant.entities.button import Button
    from quant.impl.events.event import EventTypes

import quant.utils.asyncio_utils as asyncio_utils
from quant.entities.factory import EventFactory
from quant.entities.factory.event_controller import EventController
from quant.utils.cache.cache_manager import CacheManager
from quant.utils import logger
from quant.entities.interactions.slash_option import ApplicationCommandOption
from quant.entities.gateway import GatewayInfo
from quant.entities.interactions.component_types import ComponentType
from quant.impl.core.shard import Shard
from quant.entities.interactions.interaction import Interaction
from quant.entities.snowflake import Snowflake
from quant.entities.user import User
from quant.impl.events.bot.exception_event import QuantExceptionEvent
from quant.impl.events.bot.ready_event import ReadyEvent
from quant.entities.interactions.interaction import InteractionType
from quant.entities.modal.modal import Modal
from quant.impl.core.commands import SlashCommand, SlashSubCommand, SlashSubGroup
from quant.entities.interactions.slash_option import SlashOptionType
from quant.impl.core.context import InteractionContext, ModalContext, ButtonContext
from quant.impl.events.bot.interaction_create_event import InteractionCreateEvent
from quant.impl.core.gateway import Gateway
from quant.entities.intents import Intents
from quant.impl.core.exceptions.library_exception import DiscordException
from quant.impl.core.rest import RESTImpl
from quant.impl.events.event import Event, InternalEvent, DiscordEvent
from quant.entities.model import BaseModel
from quant.entities.activity import ActivityData
from quant.utils.cache.cacheable import CacheableType

CoroutineT = TypeVar("CoroutineT", bound=Callable[..., Coroutine[Any, Any, Any]])


class Client:
    """A main bot class for interacting with Discord

    Parameters
    ----------
    token: :class:`str`
        The authentication token required for the bot to connect to Discord.
    intents: :class:`Intents`
        The intents to be used by the bot
    mobile: :class:`bool`
        Specifies whether the bot is running in a mobile environment

    Attributes
    ----------
    me: :class:`User | None`
        The user object representing the bot itself.
    shards: :class:`List[Shard]`
        The list of shards the bot is connected to.
    token: :class:`str`
        The authentication token provided during initialization.
    intents: :class:`Intents`
        The intents used by the bot.
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop used by the bot.
    cache: :class:`CacheManager`
        The cache manager used for caching Discord objects.
    event_factory: :class:`EventFactory`
        The event factory used for creating events.
    event_controller: :class:`EventController`
        The event controller used for managing events.
    rest: :class:`RESTImpl`
        The REST implementation used for interacting with the Discord REST API.
    client_id: :class:`int`
        The ID of the bot client.
    gateway: :class:`Gateway | None`
        The gateway used for communicating with Discord.
    mobile: :class:`bool`
        Specifies whether the bot is running in a mobile environment.
    asyncio_debug: :class:`bool`
        Enable asyncio debug or no
    sync_commands: :class:`bool`
        Sync application commands or no. If False, syncing will be disabled
    """
    T = TypeVar("T")

    def __init__(
        self,
        token: str,
        intents: Intents = Intents.ALL_UNPRIVILEGED,
        mobile: bool = False,
        asyncio_debug: bool = False,
        sync_commands: bool = True,
        cacheable: CacheableType = CacheableType.ALL
    ) -> None:
        self.me: User | None = None
        self.shards: List[Shard] = []
        self.token = token
        self.intents = intents
        self.loop = asyncio_utils.get_loop()
        self.cache = CacheManager(cacheable=cacheable)
        self.event_factory = EventFactory(self.cache)
        self.event_controller = EventController(self.event_factory)
        self.rest = RESTImpl(token, cache=self.cache)
        self.client_id: int = self._decode_token_to_id()
        self.gateway: Gateway | None = None
        self.mobile = mobile
        self.asyncio_debug = asyncio_debug
        self.sync_commands = sync_commands
        self._gateway_info: GatewayInfo = self.loop.run_until_complete(self.rest.get_gateway())

        self._modals: Dict[str, Modal] = {}
        self._buttons: Dict[str, Button] = {}
        self._slash_commands: Dict[str, ApplicationCommandObject | CoroutineT] = {}

        self.handlers: Dict[InteractionType, CoroutineT] = {
            InteractionType.MODAL_SUBMIT: self.handle_modal_submit,
            InteractionType.APPLICATION_COMMAND: self.handle_application_command,
            InteractionType.MESSAGE_COMPONENT: self.handle_message_components
        }

        self.add_listener(InteractionCreateEvent, self._listen_interaction_create)

    @property
    def slash_commands(self) -> Dict[str, ApplicationCommandObject | CoroutineT]:
        return self._slash_commands

    @property
    def modals(self) -> Dict[str, Modal]:
        return self._modals

    @property
    def buttons(self) -> Dict[str, Button]:
        return self._buttons

    @property
    def gateway_info(self) -> GatewayInfo:
        return self._gateway_info

    @property
    def me(self) -> User:
        return self.me

    @me.setter
    def me(self, value: User) -> None:
        self.me = value

    def _decode_token_to_id(self) -> int:
        first_token_part = self.token.split('.')[0]
        token = first_token_part[4:] \
            if first_token_part.startswith('Bot') \
            else first_token_part
        decoded_token = base64.b64decode(token + "==")
        return int(decoded_token.decode("utf8"))

    async def _run_one_shard(self, shard_count: int, shard_id: int, loop: asyncio.AbstractEventLoop) -> Shard:
        BaseModel.set_client(self)

        if loop is not None:
            self.loop = loop

        if self.asyncio_debug:
            self.loop.set_debug(self.asyncio_debug)

        shard = Shard(num_shards=shard_count, shard_id=shard_id, intents=self.intents, mobile=self.mobile)
        await shard.start(client=self, loop=self.loop)

        return shard

    def run(self, loop: asyncio.AbstractEventLoop = None) -> None:
        """Run bot

        It will run one shard with ID 0
        """
        self.run_with_shards(shard_count=1, loop=loop)

    def run_with_shards(self, shard_count: int, loop: asyncio.AbstractEventLoop = None) -> None:
        """Run bot with custom shard_count.

        Parameters
        ==========
        shard_count: :class:`int`
            Shard count with you want start bot
        loop: :class:`asyncio.AbstractEventLoop`
            Your loop if needed
        """
        for shard_id in range(shard_count):
            self.shards.append(Shard(
                num_shards=shard_count,
                shard_id=shard_id,
                intents=self.intents,
                mobile=self.mobile
            ))

        max_concurrency = self._gateway_info.session_start_limit.max_concurrency
        for i in range(0, len(self.shards), max_concurrency):
            queue_shards = self.shards[i:i + max_concurrency]

            for queued_shard in queue_shards:
                shard = self.loop.run_until_complete(self._run_one_shard(
                    shard_count=shard_count,
                    shard_id=queued_shard.shard_id,
                    loop=loop
                ))

                self.shards[queued_shard.shard_id] = shard

            asyncio.ensure_future(asyncio.sleep(5), loop=self.loop)

        self._run_forever()

    def run_autoshard(self, loop: asyncio.AbstractEventLoop = None) -> None:
        """Run autosharded bot

        Parameters
        ==========
        loop: :class:`asyncio.AbstractEventLoop`
            Your loop if needed
        """
        self.run_with_shards(shard_count=self._gateway_info.shards, loop=loop)

    def _run_forever(self) -> None:
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down bot")
            tasks = asyncio.all_tasks(loop=self.loop)

            for task in tasks:
                task.cancel()

            for shard in self.shards:
                self.loop.run_until_complete(shard.gateway.close())

            asyncio.gather(*tasks)
            asyncio_utils.kill_loop()
            logger.info("Goodbye.")
        finally:
            logger.info("Fully terminated")

    @overload
    def add_listener(self, event: T, coro: CoroutineT) -> None:
        ...

    @overload
    def add_listener(self, coro: CoroutineT) -> None:
        ...

    def add_listener(self, *args) -> None:
        """Adds listener to bot

        Examples
        --------
        .. highlight:: python
            :linenothreshold: 5

        With two arguments: ::

            async def my_message_handler(event):
                print(event.message.content)

            client.add_listener(MessageCreateEvent, my_message_handler)

        With one argument: ::

            async def my_message_handler(event: MessageCreateEvent):
                print(event.message.content)

            client.add_listener(my_message_handler)
        """
        if len(args) == 1:
            self._add_listener_from_coro(args[0])
        else:
            event, coro = args
            self._add_listener_from_event_and_coro(event, coro)

    def _add_listener_from_event_and_coro(self, event: T, coro: CoroutineT) -> None:
        if inspect.iscoroutine(coro):
            raise DiscordException("Callback function must be coroutine")

        if not issubclass(event, Event):
            raise DiscordException(f"Subclass of event {event} must be BaseEvent")

        self.event_factory.add_event(event, coro)

    def _add_listener_from_coro(self, coro: CoroutineT) -> None:
        if inspect.iscoroutine(coro):
            raise DiscordException("Callback function must be coroutine")

        try:
            type_hints = get_type_hints(coro)
            event_type = list(type_hints.values())[0]

            if isinstance(event_type, str):
                raise DiscordException("Can't handle an event class. Try .add_listener(EventType, function)")
            if not issubclass(event_type, (InternalEvent, Event, DiscordEvent)):
                raise DiscordException(f"{event_type.__name__} must be subclass of Event")

            self.event_factory.add_event(event_type, coro)
        except IndexError:
            raise DiscordException(f"You must provide which event you need {coro}")

    def remove_slash_command(self, *commands, app_id: Snowflake | int | None = None) -> None:
        """Removes slash commands

        Parameters
        ==========
        commands: :class:`SlashCommand`
            Your command/s which will be added
        app_id: :class:`Snowflake | int`
            Custom application ID
        """

        # if len(self.slash_commands) == 100:
        #     raise DiscordException("You can't create more than 100 slash commands.")

        # for command in commands:
        #     if command.id in self.slash_commands
        raise NotImplementedError

    def _add_client_slash_command(self, command: ApplicationCommandObject) -> None:
        self.slash_commands[command.name] = command

    def _register_command(self, command: SlashCommand, synced_guilds: List[int], app_id: int) -> None:
        self._add_client_slash_command(command)

        if not inspect.iscoroutinefunction(command.callback_func):
            raise DiscordException("Callback function must be coroutine")

        command_data = self.rest.entity_factory.serialize_application_command(command)

        if app_id is not None:
            command_data["application_id"] = app_id

        application_command: ApplicationCommandObject | None = None
        guild_ids = command.guild_ids
        if guild_ids:
            for guild_id in guild_ids:
                if guild_id not in synced_guilds:
                    self.loop.run_until_complete(self._sync_application_commands(guild_id=guild_id))
                    synced_guilds.append(guild_id)

                application_command: ApplicationCommandObject = self.loop.run_until_complete(
                    self.rest.create_guild_application_command(
                        **command_data,
                        guild_id=guild_id
                    )
                )
        else:
            application_command: ApplicationCommandObject = self.loop.run_until_complete(
                self.rest.create_application_command(**command_data)
            )

        application_command.options = command.options
        application_command.set_callback(command.callback_func)
        self._add_client_slash_command(application_command)

    def add_slash_command(self, commands: List[SlashCommand] | SlashCommand, app_id: Snowflake | int = None) -> None:
        """Adds your slash commands

        Parameters
        ==========
        commands: :class:`SlashCommand`
            Your command/s which will be added
        app_id: :class:`Snowflake | int`
            Custom application ID or bot client ID
        """
        app_id = self.client_id if app_id is None else app_id
        if len(self.slash_commands) == 100:
            raise DiscordException("You can't create more than 100 slash commands.")

        synced_guilds = []

        self.loop.run_until_complete(self._sync_application_commands())

        if isinstance(commands, SlashCommand):
            self._register_command(commands, app_id=app_id, synced_guilds=synced_guilds)

        elif isinstance(commands, list):
            for command in commands:
                self._register_command(command=command, app_id=app_id, synced_guilds=synced_guilds)

        else:
            raise DiscordException(f"Can't add commands because of invalid type")

    async def _sync_application_commands(self, guild_id: Snowflake | None = None) -> None:
        if self.sync_commands is False:
            return

        if guild_id is not None:
            await self.rest.bulk_overwrite_guild_app_commands(self.client_id, guild_id)
            return

        await self.rest.bulk_overwrite_global_app_commands(self.client_id)

    def add_modal(self, *modals: Modal) -> None:
        """Adds your modals

        Parameters
        ==========
        modals: :class:`Modal`
            Your modal/s which will be added
        """
        for modal in modals:
            if inspect.iscoroutine(modal.callback):
                raise DiscordException("Callback function must be coroutine")

            self.modals[str(modal.custom_id)] = modal

    def add_button(self, *buttons: Button) -> None:
        """Adds your buttons

        Parameters
        ==========
        buttons: :class:`Button`
            Your button/s which will be added
        """
        for button in buttons:
            if inspect.iscoroutine(button.callback):
                raise DiscordException("Callback function must be coroutine")

            self._buttons[str(button.custom_id)] = button

    @staticmethod
    def _handle_sub_command(options: List[ApplicationCommandOption]) -> Callable:
        for option in options:
            if option.type == SlashOptionType.SUB_COMMAND:
                return option.callback_func

    async def handle_application_command(self, interaction: Interaction) -> None:
        context = InteractionContext(self, interaction)
        command_name = interaction.data.name

        if command_name not in self.slash_commands.keys():
            return

        command = self.slash_commands[command_name]

        if interaction.data.options is not None:
            used_subcommand = interaction.data.options[0]

            for option in command.options:
                if used_subcommand.name != option.name:
                    continue

                match option.type:
                    case SlashOptionType.SUB_COMMAND:
                        await option.callback_func(context)
                    case SlashOptionType.SUB_COMMAND_GROUP:
                        callback = self._handle_sub_command(option.options)
                        command.callback_func = callback

        await command.callback_func(context)

    async def handle_modal_submit(self, interaction: Interaction) -> None:
        if interaction.data is None:
            return

        context = ModalContext(self, interaction)
        custom_id = interaction.data.custom_id

        if custom_id in self.modals.keys():
            modal = self.modals[custom_id]

            if modal.callback is not modal.callback_func:
                modal.set_callback(modal.callback)

            await modal.callback_func(context)

    async def handle_message_components(self, interaction: Interaction) -> None:
        component_type = interaction.data.component_type
        custom_id = interaction.data.custom_id

        match component_type:
            case ComponentType.BUTTON:
                if custom_id in self.buttons.keys():
                    button = self.buttons[custom_id]

                    if button.callback is not button.callback_func:
                        button.set_callback(button.callback)

                    await button.callback_func(ButtonContext(self, interaction, button))

    async def _listen_interaction_create(self, event: InteractionCreateEvent):
        interaction = event.interaction

        try:
            handler = self.handlers.get(interaction.type)
            if handler is not None:
                await handler(interaction)
        except Exception as e:
            await self.event_controller.dispatch(
                self.event_factory.build_from_class(
                    QuantExceptionEvent(), InteractionContext(self, interaction), e
                )
            )
            raise e

    async def set_activity(self, activity: ActivityData):
        """|coro|

        Sets an activity for all shards

        Parameters
        =========
        activity: :class:`ActivityData`
            Activity which will be set
        """
        presence = {
            "activity": activity.activity,
            "afk": activity.afk,
            "status": activity.status,
            "since": activity.since
        }

        for shard in self.shards:
            if shard.gateway is None:
                continue

            await shard.gateway.send_presence(**presence)

    def get_component(self, custom_id: str) -> Modal | Button:
        if (modal := self.modals.get(custom_id)) is not None:
            return modal

        if (button := self.buttons.get(custom_id)) is not None:
            return button
