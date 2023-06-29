from typing import Literal, Final
from dataclasses import dataclass


@dataclass
class URI:
    url_string: str


@dataclass
class Route:
    method: Literal["GET", "POST", "PUT", "DELETE"]
    uri: URI

    API_VERSION: Final[int] = 10

    def __str__(self) -> str:
        return self.uri.url_string

    def __invert__(self) -> str:
        return DISCORD_MAIN_API_URL + str(self)  # useless but why not)


DISCORD_MAIN_API_URL: Final[str] = "https://discord.com/api/v{}".format(Route.API_VERSION)
DISCORD_WS_URL: Final[Route] = Route(
    "GET", URI("wss://gateway.discord.gg/?v={}&encoding=json&compress=zlib-stream".format(Route.API_VERSION))
)

# Messages
CREATE_MESSAGE: Final[str] = ~Route("POST", URI("/channels/{}/messages"))
DELETE_MESSAGE: Final[str] = ~Route("DELETE", URI("/channels/{channel_id}/messages/{message_id}"))

# Webhooks
CREATE_WEBHOOK: Final[str] = ~Route("POST", URI("/channels/{channel_id}/webhooks"))
GET_CHANNEL_WEBHOOKS: Final[str] = ~Route("GET", URI("/channels/{channel_id}/webhooks"))
