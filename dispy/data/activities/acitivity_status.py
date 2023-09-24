import enum


class ActivityStatus(enum.Enum):
    ONLINE = "online"
    DO_NOT_DISTRIBUTE = "dnd"
    IDLE = "idle"
    OFFLINE = "offline"

    DND = DO_NOT_DISTRIBUTE
    AFK = IDLE
    INVISIBLE = OFFLINE
