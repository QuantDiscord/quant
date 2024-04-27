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
from __future__ import annotations

from typing import List, TYPE_CHECKING, Dict, TypeVar

if TYPE_CHECKING:
    from quant.entities.factory.entity_factory import EntityFactory
    from quant.entities.user import User
    from quant.entities.message import Message

from quant.entities.snowflake import Snowflake, SnowflakeOrInt
from quant.entities.voice_state_update import VoiceState
from quant.entities.guild import Guild
from quant.entities.emoji import Emoji, Reaction
from quant.entities.channel import Channel
from quant.utils.cache.cacheable import CacheableType
from quant.entities.roles import GuildRole, empty_role


class CacheManager:
    __cached_guilds: Dict[SnowflakeOrInt, Guild] = {}
    __cached_users: Dict[SnowflakeOrInt, User] = {}
    __cached_messages: Dict[SnowflakeOrInt, Message] = {}
    __cached_emojis: Dict[SnowflakeOrInt, Emoji | Reaction] = {}
    __cached_components: List = []
    __cached_channels: Dict[SnowflakeOrInt, Channel] = {}
    __cached_roles: Dict[SnowflakeOrInt, GuildRole] = {}

    def __init__(self, cacheable: CacheableType) -> None:
        self.cacheable = cacheable

    def add_user(self, user: User):
        """Adds user to cache."""
        self.__cached_users[user.id] = user

    def add_message(self, message: Message):
        """Adds message to cache."""
        self.__cached_messages[message.id] = message

    def add_guild(self, guild: Guild):
        """Adds guild to cache."""
        self.__cached_guilds[guild.id] = guild

    def add_emoji(self, emoji: Emoji | Reaction):
        """Adds emoji to cache."""
        if isinstance(emoji, Emoji):
            self.__cached_emojis[emoji.id] = emoji
        elif isinstance(emoji, Reaction):
            self.__cached_emojis[emoji.emoji.emoji_id] = emoji

    def add_component(self, component):
        self.__cached_components.append(component)

    def add_channel(self, channel: Channel):
        self.__cached_channels[channel.id] = channel

    def add_role(self, role: GuildRole):
        self.__cached_roles[role.id] = role

    def get_user(self, user_id: SnowflakeOrInt) -> User | None:
        """Get user from cache."""
        if user_id not in self.__cached_users:
            return

        return self.__cached_users[user_id]

    def get_member(self, guild_id: SnowflakeOrInt, member_id: SnowflakeOrInt):
        """Get member from guild"""
        member_list = self.get_guild(guild_id=guild_id).members
        for member in member_list:
            if member.id == member_id:
                return member

    def get_users(self) -> List[User]:
        """Get all cached users."""
        return list(self.__cached_users.values())

    def get_message(self, message_id: SnowflakeOrInt) -> Message | None:
        """Get message from cache."""
        if message_id not in self.__cached_messages:
            return

        return self.__cached_messages[message_id]

    def get_messages(self) -> List[Message]:
        """Get all cached message."""
        return list(self.__cached_messages.values())

    def get_guild(self, guild_id: SnowflakeOrInt) -> Guild | None:
        """Get guild from cache."""
        if guild_id not in self.__cached_guilds:
            return

        return self.__cached_guilds[guild_id]

    def get_guilds(self) -> List[Guild]:
        """Get all cached guilds."""
        return list(self.__cached_guilds.values())

    def get_emoji(self, emoji_id: SnowflakeOrInt) -> Emoji | Reaction:
        """Get emoji from cache."""
        return self.__cached_emojis[emoji_id]

    def get_channel(self, channel_id: SnowflakeOrInt) -> Channel:
        """Get channel from cache"""
        return self.__cached_channels[channel_id]

    def get_emojis(self) -> List[Emoji | Reaction]:
        """Get all cached emojis"""
        return list(self.__cached_emojis.values())

    def get_voice_state(self, guild_id: int, user_id: int) -> VoiceState:
        """Getting voice state where user in"""
        guild = self.get_guild(guild_id)

        return [state for state in guild.voice_states
                if state.guild_id == state.guild_id and state.user_id == user_id][0]

    def get_role(self, role_id: Snowflake | int) -> GuildRole:
        try:
            return self.__cached_roles[role_id]
        except KeyError:
            return empty_role()


class CacheHandlers(CacheManager):
    def __init__(self, factory: EntityFactory, cacheable: CacheableType) -> None:
        self.entity_factory = factory
        super().__init__(cacheable=cacheable)

    def handle_ready(self, **kwargs) -> None:
        self.add_user(self.entity_factory.deserialize_user(kwargs))

    def handle_user(self, **kwargs) -> None:
        self.add_user(self.entity_factory.deserialize_user(kwargs))

    def handle_message(self, **kwargs) -> None:
        if not self.cacheable & CacheableType.MESSAGE:
            return

        self.add_message(self.entity_factory.deserialize_message(kwargs))

    def handle_guild(self, **kwargs) -> None:
        if not self.cacheable & CacheableType.GUILD:
            return

        guild_object = self.entity_factory.deserialize_guild(kwargs)
        self.add_guild(guild_object)

        if self.cacheable & CacheableType.ROLE:
            for role in guild_object.roles:
                self.add_role(role)

        if self.cacheable & CacheableType.CHANNEL:
            for channel in guild_object.channels:
                self.add_channel(channel)

        if self.cacheable & CacheableType.EMOJI:
            for emoji in guild_object.emojis:
                self.add_emoji(emoji)

        guild_object.members = [
            self.entity_factory.deserialize_member(member_data, Snowflake(guild_object.id))
            for member_data in kwargs.get("members", [])
        ]

        if self.cacheable & CacheableType.USER:
            for member in guild_object.members:
                self.add_user(member.user)

    def handle_guild_delete(self, **kwargs) -> None:
        guild_id = Snowflake(kwargs.get("id"))

        if guild_id in self.__cached_guilds:
            del self.__cached_guilds[Snowflake(kwargs["id"])]

    def handle_voice_state_update(self, **kwargs) -> None:
        state = self.entity_factory.deserialize_voice_state(kwargs)
        guild = self.get_guild(state.guild_id)

        if len(guild.voice_states) == 0:
            guild.voice_states.append(state)

    def handle_channel_create(self, **kwargs) -> None:
        self.add_channel(self.entity_factory.deserialize_channel(kwargs))
