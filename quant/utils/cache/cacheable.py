import enum


class CacheableType(enum.IntFlag):
    USER = 1 << 1
    ROLE = 1 << 2
    GUILD = 1 << 3
    MESSAGE = 1 << 4
    EMOJI = 1 << 5
    CHANNEL = 1 << 6

    ALL = USER | ROLE | GUILD | MESSAGE | EMOJI | CHANNEL
