import enum


class WebhookTypes(enum.Enum):
    INCOMING = 1
    CHANNEL_FOLLOWER = 2
    APPLICATION = 3
