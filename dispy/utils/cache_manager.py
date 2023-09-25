from typing import Dict, Any, List

from dispy.data.user import User
from dispy.data.guild.guild_object import Guild
from dispy.data.guild.messages.emoji import Emoji, Reaction
from dispy.data.guild.messages.message import Message
from dispy.impl.events.types import EventTypes


class CacheManager:
    __cached_guilds: Dict[int, Any] = {}
    __cached_users: Dict[int, User] = {}
    __cached_messages: Dict[int, Message] = {}
    __cached_emojis: Dict[int, Emoji | Reaction] = {}

    def add_user(self, user: User):
        self.__cached_users[user.user_id] = user

    def add_message(self, message: Message):
        self.__cached_messages[message.message_id] = message

    def add_guild(self, guild: Guild):
        self.__cached_guilds[guild.guild_id] = guild

    def add_emoji(self, emoji: Emoji | Reaction):
        if isinstance(emoji, Emoji):
            self.__cached_emojis[emoji.emoji_id] = emoji
        elif isinstance(emoji, Reaction):
            self.__cached_emojis[emoji.emoji.emoji_id] = emoji

    def get_user(self, user_id: int) -> User | None:
        return self.__cached_users.get(user_id)

    def get_users(self) -> List[User]:
        return list(self.__cached_users.values())

    def get_message(self, message_id: int) -> Message | None:
        return self.__cached_messages.get(message_id)

    def get_messages(self) -> List[Message]:
        return list(self.__cached_messages.values())

    def get_guild(self, guild_id: int) -> Guild | None:
        return self.__cached_guilds.get(guild_id)

    def get_guilds(self) -> List[Guild]:
        return list(self.__cached_guilds.values())

    def get_emoji(self, emoji_id: int) -> Emoji | Reaction:
        return self.__cached_emojis.get(emoji_id)

    def get_emojis(self) -> List[Emoji | Reaction]:
        return list(self.__cached_emojis.values())

    # тут вроде ошибка была или какие-то конфликты, надо будет пересмотреть
    def add_from_event(self, event_name, **data):
        match event_name:
            case EventTypes.MESSAGE_CREATE:
                self.add_message(Message(**data))
            case EventTypes.GUILD_CREATE:
                guild_object = Guild(**data)
                self.add_guild(guild_object)

                if guild_object.member_count <= 2000:
                    for member in guild_object.members:
                        self.add_user(member.user)

                for emoji in guild_object.emojis:
                    self.add_emoji(Emoji(**emoji))
            case EventTypes.GUILD_DELETE:
                del self.__cached_guilds[int(data["id"])]

# мама сказала, что я умный
