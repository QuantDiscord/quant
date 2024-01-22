from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from quant.entities.factory.entity_factory import EntityFactory

from quant.api.entities.component import Component
from quant.entities.snowflake import Snowflake
from quant.utils.json_builder import MutableJsonBuilder
from quant.entities.voice_state_update import VoiceState
from quant.entities.user import User
from quant.entities.guild import Guild
from quant.entities.emoji import Emoji, Reaction
from quant.entities.message import Message
from quant.entities.channel import Channel
from quant.utils.cache.cacheable import CacheableType


class CacheManager:
    __cached_guilds: MutableJsonBuilder[Snowflake, Guild] = MutableJsonBuilder()
    __cached_users: MutableJsonBuilder[Snowflake, User] = MutableJsonBuilder()
    __cached_messages: MutableJsonBuilder[Snowflake, Message] = MutableJsonBuilder()
    __cached_emojis: MutableJsonBuilder[Snowflake, Emoji | Reaction] = MutableJsonBuilder()
    __cached_components: List[Component] = []
    __cached_channels: MutableJsonBuilder[Snowflake, Channel] = MutableJsonBuilder()

    def __init__(self, cacheable: CacheableType | None = None) -> None:
        self.cacheable = cacheable.value if cacheable is not None else None

    def add_user(self, user: User):
        """Adds user to cache."""
        self.__cached_users.put(user.id, user)

    def add_message(self, message: Message):
        """Adds message to cache."""
        self.__cached_messages.put(message.id, message)

    def add_guild(self, guild: Guild):
        """Adds guild to cache."""
        self.__cached_guilds.put(guild.id, guild)

    def add_emoji(self, emoji: Emoji | Reaction):
        """Adds emoji to cache."""
        if isinstance(emoji, Emoji):
            self.__cached_emojis.put(emoji.id, emoji)
        elif isinstance(emoji, Reaction):
            self.__cached_emojis.put(emoji.emoji.emoji_id, emoji)

    def add_component(self, component: Component):
        self.__cached_components.append(component)

    def add_channel(self, channel: Channel):
        self.__cached_channels.put(channel.id, channel)

    def get_user(self, user_id: int) -> User | None:
        """Get user from cache."""
        return self.__cached_users[user_id]

    def get_users(self) -> List[User]:
        """Get all cached users."""
        return list(self.__cached_users.get_values())

    def get_message(self, message_id: int) -> Message | None:
        """Get message from cache."""
        return self.__cached_messages[message_id]

    def get_messages(self) -> List[Message]:
        """Get all cached message."""
        return list(self.__cached_messages.get_values())

    def get_guild(self, guild_id: int | Snowflake) -> Guild | None:
        """Get guild from cache."""
        return self.__cached_guilds[guild_id]

    def get_guilds(self) -> List[Guild]:
        """Get all cached guilds."""
        return list(self.__cached_guilds.get_values())

    def get_emoji(self, emoji_id: int) -> Emoji | Reaction:
        """Get emoji from cache."""
        return self.__cached_emojis[emoji_id]

    def get_channel(self, channel_id: int) -> Channel:
        """Get channel from cache"""
        return self.__cached_channels[channel_id]

    def get_emojis(self) -> List[Emoji | Reaction]:
        """Get all cached emojis"""
        return list(self.__cached_emojis.get_values())

    def get_component(self) -> List[Component]:
        """Get all cached components"""
        return self.__cached_components

    def get_voice_state(self, guild_id: int, user_id: int) -> VoiceState:
        """Getting voice state where user in"""
        guild = self.get_guild(guild_id)

        return [state for state in guild.voice_states
                if state.guild_id == state.guild_id and state.user_id == user_id][0]


class CacheHandlers(CacheManager):
    def __init__(self, factory: EntityFactory) -> None:
        self.entity_factory = factory
        super().__init__()

    def handle_ready(self, **kwargs) -> None:
        self.add_user(self.entity_factory.deserialize_user(kwargs))

    def handle_message(self, **kwargs) -> None:
        self.add_message(Message(**kwargs))

    def handle_guild(self, **kwargs) -> None:
        guild_object = self.entity_factory.deserialize_guild(kwargs)
        self.add_guild(guild_object)

        for channel in guild_object.channels:
            self.add_channel(channel)

        for emoji in guild_object.emojis:
            self.add_emoji(self.entity_factory.deserialize_emoji(emoji))

    def handle_guild_delete(self, **kwargs) -> None:
        del self.__cached_guilds[int(kwargs["id"])]

    def handle_voice_state_update(self, **kwargs) -> None:
        guild_id = kwargs.get('guild_id')
        guild = self.get_guild(int(guild_id))
        state = self.entity_factory.deserialize_voice_state(kwargs)

        if len(guild.voice_states) == 0:
            guild.voice_states.append(state)

    def handle_channel_create(self, **kwargs) -> None:
        self.add_channel(self.entity_factory.deserialize_channel(kwargs))

# мама сказала, что я умный (fr)
