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

import enum
from typing import TYPE_CHECKING, List

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.entities.snowflake import Snowflake


class ActivityStatus(enum.Enum):
    """Discord activity statuses"""
    ONLINE = "online"
    DO_NOT_DISTRIBUTE = "dnd"
    IDLE = "idle"
    OFFLINE = "offline"

    DND = DO_NOT_DISTRIBUTE
    AFK = IDLE
    INVISIBLE = OFFLINE


class ActivityFlags(enum.IntFlag):
    """Discord activity flags"""
    INSTANCE = 1 << 0
    JOIN = 1 << 1
    SPECTATE = 1 << 2
    JOIN_REQUEST = 1 << 3
    SYNC = 1 << 4
    PLAY = 1 << 5
    PARTY_PRIVACY_FRIENDS = 1 << 6
    PARTY_PRIVACY_VOICE_CHANNEL = 1 << 7
    EMBEDDED = 1 << 8


class ActivityType(enum.IntEnum):
    """Discord activity types"""
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


@attrs.define(hash=True)
class Activity:
    """Represents a discord activity

    Parameters
    ==========
    name: :class:`str`
        Activity name
    url: :class:`str | None`
        Activity url (twitch for example)
    type: :class:`ActivityType`
        Activity type
    created_at: :class:`float`
        Activity created at timestamp
    state: :class:`str | None`
        State text
    details: :class:`ActivityType`
        Details text
    """
    name: str | None = attrs.field(default=None)
    created_at: float = attrs.field(default=None)
    url: str | None = attrs.field(default=None)
    type: ActivityType = attrs.field(default=ActivityType.GAME)
    timestamps: List = attrs.field(default=None)
    application_id: Snowflake = attrs.field(default=None)
    details: str = attrs.field(default=None)
    state: str = attrs.field(default=None)
    emoji: str = attrs.field(default=None)


@attrs.define(hash=True)
class ActivityAssets:
    """Represents activity assets (image, text)

    Parameters
    ==========
    large_image: :class:`str`
        Large activity image
    large_text: :class:`str`
        Large activity text
    small_image: :class:`str`
        Small activity image
    small_text: :class:`str`
        Small activity text

    """
    large_image: str = attrs.field(default=None)
    large_text: str = attrs.field(default=None)
    small_image: str = attrs.field(default=None)
    small_text: str = attrs.field(default=None)


@attrs.define(hash=True)
class ActivityData:
    """Activity data

    Parameters
    =========
    activity: :class:`Activity`
        Setting up main activity
    status: :class:`ActivityStatus`
        Setting up activity status
    since: :class:`int | None`
        Time since enabled
    afk: :class:`bool`
        Is AFK or no
    """
    activity: Activity | None = attrs.field(default=None)
    status: ActivityStatus | None = attrs.field(default=None)
    since: int | None = attrs.field(default=None)
    afk: bool | None = attrs.field(default=None)


class ActivityBuilder:
    """Build an activity

    .. attributetable:: ActivityBuilder
    """

    def __init__(self) -> None:
        self._activity: Activity | None = None
        self._status: ActivityStatus | None = None
        self._since: int | None = None
        self._afk: bool | None = None

    def set_activity(
        self,
        name: str | None = None,
        url: str | None = None,
        created_at: float = None,
        activity_type: ActivityType = ActivityType.GAME,
        application_id: Snowflake | None = None,
        details: str | None = None,
        state: str | None = None,
        emoji: str | None = None,
    ) -> Self:
        """Set an activity"""
        self._activity = Activity(
            name=name,
            url=url,
            type=activity_type,
            created_at=created_at,
            application_id=application_id,
            details=details,
            state=state,
            emoji=emoji
        )
        return self

    def set_status(self, status: ActivityStatus) -> Self:
        """Build status"""
        self._status = status
        return self

    def set_since(self, value: int) -> Self:
        """Set since value"""
        self._since = value
        return self

    def set_afk(self, value: bool) -> Self:
        """Set AFK value"""
        self._afk = value
        return self

    def build(self) -> ActivityData:
        """Build an ActivityData"""
        return ActivityData(
            activity=self._activity,
            status=self._status,
            since=self._since,
            afk=self._afk
        )
