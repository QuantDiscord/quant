from __future__ import annotations

import contextlib
from typing import (
    Dict,
    Any,
    Callable,
    TYPE_CHECKING,
    cast,
    TypeVar,
    List
)
from datetime import datetime

import attrs


if TYPE_CHECKING:
    from quant.utils.cache.cache_manager import CacheManager

from quant.impl import events
from quant import entities
from quant.utils.json_builder import MutableJsonBuilder
from quant.utils.cache.cache_manager import CacheHandlers
from quant.impl.events.event import Event, InternalEvent, DiscordEvent
from quant.impl.events.types import EventTypes

EventT: TypeVar = TypeVar("EventT", Event, DiscordEvent, InternalEvent)


class EventFactory:
    def __init__(self, cache_manager: CacheManager) -> None:
        self.added_listeners: Dict[EventT, Callable] = {}
        self._listener_transformer: Dict[str, EventT] = {}
        self.cache = cache_manager
        self.entity_factory = entities.factory.EntityFactory()

    def build_event(self, received_type: EventTypes, **details) -> EventT | None:
        event_type = received_type.value
        if event_type not in self._listener_transformer:
            return

        event = self._listener_transformer[event_type]
        # TODO: Это в будущем убрать надо (cache_manager)
        event_class = cast(event, self._listener_transformer[event_type])(cache_manager=self.cache)
        return event_class.emit(**details)

    @staticmethod
    def build_from_class(event: EventT, *args: Any) -> EventT | None:
        with contextlib.suppress(AttributeError):
            event.emit(*args)
            return event.build(event, *args)

    async def dispatch(self, event: EventT) -> None:
        event_callback = self.added_listeners.get(type(event))
        if event_callback is not None:
            await event_callback(event)
            return

        if event is not None:
            await event.call()
            return

    def add_event(self, event: EventT, callback: Callable) -> None:
        self.added_listeners[event] = callback

        if not hasattr(event, "event_api_name"):
            return

        fields = attrs.fields(event)
        self._listener_transformer[fields.event_api_name.default] = event

    async def wait(self, event_type: EventTypes, condition: Callable, timeout: int = 5) -> None:
        ...

    def cache_item(self, event_name: EventTypes, **kwargs) -> None:
        cache_handler = CacheHandlers(self.entity_factory)
        handlers = {
            EventTypes.READY_EVENT: cache_handler.handle_ready,
            EventTypes.MESSAGE_CREATE: cache_handler.handle_message,
            EventTypes.VOICE_STATE_UPDATE: cache_handler.handle_voice_state_update,
            EventTypes.GUILD_CREATE: cache_handler.handle_guild,
            EventTypes.GUILD_DELETE: cache_handler.handle_guild_delete,
            EventTypes.CHANNEL_CREATE: cache_handler.handle_channel_create
        }

        if handler := handlers.get(event_name):
            print(handler)
            handler(**kwargs)  # type: ignore

    def deserialize_voice_state_update_event(
        self,
        guild_id: entities.Snowflake | int,
        channel_id: entities.Snowflake | int,
        user_id: entities.Snowflake | int,
        member: entities.GuildMember | None = None,
        session_id: str | None = None,
        deaf: bool = False,
        mute: bool = False,
        self_deaf: bool = False,
        self_mute: bool = False,
        self_stream: bool = False,
        self_video: bool = False,
        suppress: bool = False,
        request_to_speak_timestamp: datetime | None = None
    ) -> events.VoiceStateUpdateEvent:
        return events.VoiceStateUpdateEvent(
            cache_manager=self.cache,
            state=entities.VoiceState(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                member=member,
                session_id=session_id,
                deaf=deaf,
                mute=mute,
                self_deaf=self_deaf,
                self_mute=self_mute,
                self_stream=self_stream,
                self_video=self_video,
                suppress=suppress,
                request_to_speak_timestamp=request_to_speak_timestamp
            )
        )

    def deserialize_voice_server_update_event(
        self,
        guild_id: entities.Snowflake | int,
        token: str | None = None,
        endpoint: str | None = None
    ) -> events.VoiceServerUpdateEvent:
        return events.VoiceServerUpdateEvent(
            cache_manager=self.cache,
            state=entities.VoiceServer(
                token=token,
                guild_id=guild_id,
                endpoint=endpoint
            )
        )

    def deserialize_reaction_create_event(
        self,
        user_id: entities.Snowflake,
        reaction_type: int,
        message_id: entities.Snowflake,
        message_author_id: entities.Snowflake,
        channel_id: entities.Snowflake,
        guild_id: entities.Snowflake,
        member: entities.GuildMember | None = None,
        emoji: entities.PartialReaction | None = None,
        burst: bool = False,
        burst_colors: List[Any] | None = None
    ) -> events.ReactionAddEvent:
        return events.ReactionAddEvent(
            cache_manager=self.cache,
            reaction=entities.Reaction(
                user_id=user_id,
                reaction_type=reaction_type,
                message_id=message_id,
                message_author_id=message_author_id,
                channel_id=channel_id,
                guild_id=guild_id,
                member=member,
                emoji=emoji,
                burst=burst,
                burst_colors=burst_colors
            )
        )

    def deserialize_reaction_remove_event(
        self,
        user_id: entities.Snowflake,
        reaction_type: int,
        message_id: entities.Snowflake,
        message_author_id: entities.Snowflake,
        channel_id: entities.Snowflake,
        guild_id: entities.Snowflake,
        member: entities.GuildMember | None = None,
        emoji: entities.PartialReaction | None = None,
        burst: bool = False,
        burst_colors: List[Any] | None = None
    ) -> events.ReactionRemoveEvent:
        return events.ReactionRemoveEvent(
            cache_manager=self.cache,
            reaction=entities.Reaction(
                user_id=user_id,
                reaction_type=reaction_type,
                message_id=message_id,
                message_author_id=message_author_id,
                channel_id=channel_id,
                guild_id=guild_id,
                member=member,
                emoji=emoji,
                burst=burst,
                burst_colors=burst_colors
            )
        )

    def deserialize_message_create_event(self, message: entities.Message) -> events.MessageCreateEvent:
        return events.MessageCreateEvent(
            cache_manager=self.cache,
            message=message
        )

    def deserialize_message_delete_event(self, message: entities.Message) -> events.MessageDeleteEvent:
        return events.MessageDeleteEvent(
            cache_manager=self.cache,
            author=message.author_as_user,
            message=message
        )

    def deserialize_message_edit_event(
        self,
        old_message: entities.Message,
        new_message: entities.Message
    ) -> events.MessageEditEvent:
        return events.MessageEditEvent(
            cache_manager=self.cache,
            old_message=old_message,
            new_message=new_message
        )

    def deserialize_guild_create_event(self, payload: MutableJsonBuilder) -> events.GuildCreateEvent:
        return events.GuildCreateEvent(
            cache_manager=self.cache,
            guild=self.entity_factory.deserialize_guild(payload)
        )

    def deserialize_interaction_event(self, interaction: entities.Interaction) -> events.InteractionCreateEvent:
        return events.InteractionCreateEvent(
            cache_manager=self.cache,
            interaction=interaction
        )
