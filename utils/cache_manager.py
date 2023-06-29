from typing import Dict, Any
from collections import OrderedDict

from dispy.data.user import User
from dispy.data.guild.messages.message import Message


class CacheManager:
    __cached_guilds: Dict[int, Any] = OrderedDict()
    __cached_users: Dict[int, User] = OrderedDict()
    __cached_messages: Dict[int, Message] = OrderedDict()

    def add_cache_user(self, user: User):
        self.__cached_users[user.user_id] = user

    def add_cache_message(self, message: Message):
        self.__cached_messages[message.message_id] = message

    def get_user(self, user_id: int) -> User:
        return self.__cached_users[user_id]

    def get_message(self, message_id: int) -> Message | None:
        if message_id in self.__cached_messages:
            return self.__cached_messages[message_id]
