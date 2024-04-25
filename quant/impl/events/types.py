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
