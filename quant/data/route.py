from typing import Literal, Final, Any

import attrs


@attrs.define
class URI:
    _url_string: str
    auto_format: bool = True

    @property
    def url_string(self) -> str:
        if not self.auto_format:
            return self._url_string
        return DISCORD_MAIN_API_URL + self._url_string


@attrs.define
class Route:
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    uri: URI
    api_version: int = 10


_ROUTE_FIELDS = attrs.fields(Route)
DISCORD_MAIN_API_URL: Final[str] = "https://discord.com/api/v{}".format(_ROUTE_FIELDS.api_version.default)
DISCORD_WS_URL: Final[Route] = Route(
    "GET", URI("wss://gateway.discord.gg/?v={}&encoding=json&compress=zlib-stream".format(_ROUTE_FIELDS.api_version.default),
               auto_format=False)
)

# Messages
GET_MESSAGE: Final[Route] = Route("GET", URI("/channels/{channel_id}/messages/{message_id}"))
CREATE_MESSAGE: Final[Route] = Route("POST", URI("/channels/{}/messages"))
DELETE_MESSAGE: Final[Route] = Route("DELETE", URI("/channels/{channel_id}/messages/{message_id}"))
CREATE_REACTION: Final[Route] = Route("PUT", URI("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"))
GET_GUILD_EMOJI: Final[Route] = Route("GET", URI("/guilds/{guild_id}/emojis/{emoji_id}"))

# Webhooks
CREATE_WEBHOOK: Final[Route] = Route("POST", URI("/channels/{channel_id}/webhooks"))
GET_CHANNEL_WEBHOOKS: Final[Route] = Route("GET", URI("/channels/{channel_id}/webhooks"))

# Guilds
GET_GUILD: Final[Route] = Route("GET", URI("/guilds/{guild_id}"))
CREATE_GUILD: Final[Route] = Route("POST", URI("/guilds"))
DELETE_GUILD: Final[Route] = Route("DELETE", URI("/guilds/{guild_id}"))

# Interactions
CREATE_INTERACTION_RESPONSE: Final[Route] = Route(
    "POST", URI("/interactions/{interaction_id}/{interaction_token}/callback")
)
GET_ORIGINAL_INTERACTION_RESPONSE: Final[Route] = Route(
    "GET", URI("/webhooks/{application_id}/{interaction_token}/messages/@original")
)
EDIT_ORIGINAL_INTERACTION_RESPONSE: Final[Route] = Route(
    "PATCH", URI("/webhooks/{application_id}/{interaction_token}/messages/@original")
)
DELETE_ORIGINAL_INTERACTION_RESPONSE: Final[Route] = Route(
    "DELETE", URI("/webhooks/{application_id}/{interaction_token}/messages/@original")
)

# Followups later

# Channels
GET_CHANNEL_MESSAGES: Final[Route] = Route("GET", URI("/channels/{channel_id}/messages"))
