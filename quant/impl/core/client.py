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
    TYPE_CHECKING
)

from quant.entities.factory import EventFactory
from quant.entities.factory.event_controller import EventController
from quant.utils.cache.cache_manager import CacheManager

if TYPE_CHECKING:
    from quant.entities.button import Button

import quant.utils.asyncio_utils as asyncutil
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
    """
    T = TypeVar("T")

    def __init__(
        self,
        token: str,
        intents: Intents = Intents.ALL_UNPRIVILEGED,
        mobile: bool = False
    ) -> None:
        self.me: User | None = None
        self.shards: List[Shard] = []
        self.token = token
        self.intents = intents
        self.loop = asyncutil.get_loop()
        self.cache = CacheManager()
        self.event_factory = EventFactory(self.cache)
        self.event_controller = EventController(self.event_factory)
        self.rest = RESTImpl(token, cache=self.cache)
        self.client_id: int = self._decode_token_to_id()
        self.gateway: Gateway | None = None
        self.mobile = mobile
        self._gateway_info: GatewayInfo = self.loop.run_until_complete(self.rest.get_gateway())

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

    async def _run_one_shard(self, shard_count: int, shard_id: int, loop: asyncio.AbstractEventLoop) -> Shard:
        BaseModel.set_client(self)

        if loop is not None:
            self.loop = loop

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

            self.loop.run_until_complete(asyncio.sleep(5))

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
            self.gateway.get_logger.info("Shutting down bot")

            for shard in self.shards:
                if shard.shard_id == 0:
                    self.loop.run_until_complete(self.gateway.close())
                    continue

                self.loop.run_until_complete(shard.gateway.close())
                asyncutil.kill_loop()

            self.gateway.get_logger.info("Goodbye. Bot terminated")

    @overload
    def add_listener(self, event: T, coro: _Coroutine) -> None:
        ...

    @overload
    def add_listener(self, coro: _Coroutine) -> None:
        ...

    def add_listener(self, *args) -> None:
        """Adds listener to bot

        Examples
        --------
        .. highlight:: python
            :linenothreshold: 5
            
        With two arguments: ::

        .. code-block:: python
            async def my_message_handler(event):
                print(event.message.content)

            client.add_listener(MessageCreateEvent, my_message_handler)

        With one argument: ::

        .. code-block:: python
            async def my_message_handler(event: MessageCreateEvent):
                print(event.message.content)

            client.add_listener(my_message_handler)
        """
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

        self.event_factory.add_event(event, coro)

    def _add_listener_from_coro(self, coro: _Coroutine) -> None:
        if inspect.iscoroutine(coro):
            raise DiscordException("Callback function must be coroutine")

        annotations = inspect.getmembers(coro)[0]
        try:
            event_type = list(annotations[1].values())[0]

            if not issubclass(event_type, (InternalEvent, Event, DiscordEvent)):
                raise DiscordException(f"{event_type.__name__} must be subclass of Event")

            self.event_factory.add_event(event_type, coro)
        except IndexError:
            raise DiscordException(f"You must provide which event you need {coro}")

    def add_slash_command(self, *commands: SlashCommand, app_id: Snowflake | int = None) -> None:
        """Adds your slash commands

        Parameters
        ==========
        commands: :class:`SlashCommand`
            Your command/s which will be added
        app_id: :class:`Snowflake | int`
            Custom application ID
        """
        for command in commands:
            if inspect.iscoroutine(command.callback):
                raise DiscordException("Callback function must be coroutine")

            if len(self.slash_commands) == 100:
                raise DiscordException("You can't create more than 100 slash commands.")

            self.slash_commands[command.name] = command

            command_data = {
                "application_id": self.client_id if app_id is None else app_id,
                "name": command.name,
                "description": command.description,
                "options": command.options
            }

            guild_ids = command.guild_ids
            if guild_ids:
                for guild_id in guild_ids:
                    asyncio.ensure_future(
                        self.rest.create_guild_application_command(
                            **command_data,
                            guild_id=guild_id
                        ),
                        loop=self.loop
                    )
                continue

            asyncio.ensure_future(
                self.rest.create_application_command(**command_data), loop=self.loop
            )

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

    @property
    def slash_commands(self) -> Dict[str, SlashCommand]:
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
                await self.gateway.send_presence(**presence)
            else:
                await shard.gateway.send_presence(**presence)

    async def _set_client_user_on_ready(self, _: ReadyEvent) -> None:
        self.me = self.cache.get_users()[0]
