from typing import Final


class _DynamicEnum:
    _values = {}

    def __init__(self, value):
        self.value = value
        _DynamicEnum._values[value] = self

    def __str__(self):
        return self.value

    @classmethod
    def get(cls, value):
        return cls._values.get(value, None)


class EventTypes(_DynamicEnum):
    MESSAGE_CREATE: Final[str] = "MESSAGE_CREATE"
    MESSAGE_DELETE: Final[str] = "MESSAGE_DELETE"
    MESSAGE_UPDATE: Final[str] = "MESSAGE_UPDATE"
    MESSAGE_REACTION_ADD: Final[str] = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE: Final[str] = "MESSAGE_REACTION_REMOVE"
    GUILD_CREATE: Final[str] = "GUILD_CREATE"
    GUILD_DELETE: Final[str] = "GUILD_DELETE"
    READY_EVENT: Final[str] = "READY"
    INTERACTION_CREATE: Final[str] = "INTERACTION_CREATE"
    VOICE_STATE_UPDATE: Final[str] = "VOICE_STATE_UPDATE"
    VOICE_SERVER_UPDATE: Final[str] = "VOICE_SERVER_UPDATE"
    CHANNEL_CREATE: Final[str] = "CHANNEL_CREATE"
    PRESENCE_UPDATE: Final[str] = "PRESENCE_UPDATE"
    TYPING_START: Final[str] = "TYPING_START"
    GUILD_MEMBER_ADD: Final[str] = "GUILD_MEMBER_ADD"
