import enum

import attrs


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
class ActivityBuilder:
    activity: Activity | None = attrs.field(default=None)
    status: ActivityStatus | None = attrs.field(default=None)
    since: int | None = attrs.field(default=None)
    afk: bool = attrs.field(default=False)


@attrs.define
class ActivityAssets:
    large_image: str = attrs.field(default=None)
    large_text: str = attrs.field(default=None)
    small_image: str = attrs.field(default=None)
    small_text: str = attrs.field(default=None)
