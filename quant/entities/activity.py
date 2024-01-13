import enum

import attrs
from typing_extensions import Self


class ActivityStatus(enum.Enum):
    ONLINE = "online"
    DO_NOT_DISTRIBUTE = "dnd"
    IDLE = "idle"
    OFFLINE = "offline"

    DND = DO_NOT_DISTRIBUTE
    AFK = IDLE
    INVISIBLE = OFFLINE


class ActivityFlags(enum.IntFlag):
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
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


@attrs.define
class Activity:
    name: str = attrs.field()
    url: str | None = attrs.field(default=None)
    type: ActivityType = attrs.field(default=ActivityType.GAME)


@attrs.define
class ActivityAssets:
    large_image: str = attrs.field(default=None)
    large_text: str = attrs.field(default=None)
    small_image: str = attrs.field(default=None)
    small_text: str = attrs.field(default=None)


@attrs.define
class ActivityData:
    activity: Activity | None = attrs.field(default=None)
    status: ActivityStatus | None = attrs.field(default=None)
    since: int | None = attrs.field(default=None)
    afk: bool | None = attrs.field(default=None)


class ActivityBuilder:
    def __init__(self) -> None:
        self._activity: Activity | None = None
        self._status: ActivityStatus | None = None
        self._since: int | None = None
        self._afk: bool | None = None

    def set_activity(
        self,
        name: str,
        url: str | None = None,
        activity_type: ActivityType = ActivityType.GAME
    ) -> Self:
        self._activity = Activity(name=name, url=url, type=activity_type)
        return self

    def set_status(self, status: ActivityStatus) -> Self:
        self._status = status
        return self

    def set_since(self, value: int) -> Self:
        self._since = value
        return self

    def set_afk(self, value: bool) -> Self:
        self._afk = value
        return self

    def build(self) -> ActivityData:
        return ActivityData(
            activity=self._activity,
            status=self._status,
            since=self._since,
            afk=self._afk
        )
