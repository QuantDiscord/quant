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
    method: str
    uri: URI
    api_version: int = 10


GET: Final[str] = "GET"
DELETE: Final[str] = "DELETE"
PATCH: Final[str] = "PATCH"
PUT: Final[str] = "PUT"
POST: Final[str] = "POST"

_ROUTE_FIELDS = attrs.fields(Route)
DISCORD_MAIN_API_URL: Final[str] = "https://discord.com/api/v{}".format(_ROUTE_FIELDS.api_version.default)
DISCORD_WS_URL: Final[Route] = Route(
    "GET", URI(
        "wss://gateway.discord.gg/?v={}&encoding=json&compress=zlib-stream".format(_ROUTE_FIELDS.api_version.default),
        auto_format=False
    )
)
GATEWAY_BOT: Final[Route] = Route("GET", URI("/gateway/bot"))

# Messages
GET_MESSAGE: Final[Route] = Route(GET, URI("/channels/{channel_id}/messages/{message_id}"))
CREATE_MESSAGE: Final[Route] = Route(POST, URI("/channels/{}/messages"))
EDIT_MESSAGE: Final[Route] = Route(PATCH, URI("/channels/{channel_id}/messages/{message_id}"))
DELETE_MESSAGE: Final[Route] = Route(DELETE, URI("/channels/{channel_id}/messages/{message_id}"))
CREATE_REACTION: Final[Route] = Route(PUT, URI("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"))
GET_GUILD_EMOJI: Final[Route] = Route(GET, URI("/guilds/{guild_id}/emojis/{emoji_id}"))
DELETE_ALL_REACTIONS: Final[Route] = Route(DELETE, URI("/channels/{channel_id}/messages/{message_id}/reactions"))
DELETE_ALL_REACTION_FOR_EMOJI: Final[Route] = Route(
    DELETE, URI("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")
)

# Webhooks
CREATE_WEBHOOK: Final[Route] = Route(POST, URI("/channels/{channel_id}/webhooks"))
GET_CHANNEL_WEBHOOKS: Final[Route] = Route(GET, URI("/channels/{channel_id}/webhooks"))

# Guilds
GET_GUILD: Final[Route] = Route(GET, URI("/guilds/{guild_id}"))
CREATE_GUILD: Final[Route] = Route(POST, URI("/guilds"))
DELETE_GUILD: Final[Route] = Route(DELETE, URI("/guilds/{guild_id}"))
CREATE_GUILD_BAN: Final[Route] = Route(PUT, URI("/guilds/{guild_id}/bans/{user_id}"))
GET_INVITE: Final[Route] = Route(GET, URI("/invites/{invite_code}"))
DELETE_INVITE: Final[Route] = Route(DELETE, URI("/invites/{invite_code}"))
GET_GUILD_INVITES: Final[Route] = Route(GET, URI("/guilds/{guild_id}/invites"))
GET_GUILD_ROLES: Final[Route] = Route(GET, URI("/guilds/{guild_id}/roles"))
CREATE_GUILD_ROLES: Final[Route] = Route(POST, URI("/guilds/{guild_id}/roles"))
DELETE_GUILD_ROLE: Final[Route] = Route(DELETE, URI("/guilds/{guild_id}/roles/{role_id}"))
GET_GUILD_MEMBERS: Final[Route] = Route(GET, URI("/guilds/{guild_id}/members"))
GET_GUILD_MEMBER: Final[Route] = Route(GET, URI("/guilds/{guild_id}/members/{user_id}"))
MODIFY_GUILD_MEMBER: Final[Route] = Route(PATCH, URI("/guilds/{guild_id}/members/{user_id}"))
REMOVE_GUILD_MEMBER: Final[Route] = Route(DELETE, URI("/guilds/{guild_id}/members/{user_id}"))
ADD_GUILD_MEMBER_ROLE: Final[Route] = Route(PUT, URI("/guilds/{guild_id}/members/{user_id}/roles/{role_id}"))

# Interactions
CREATE_INTERACTION_RESPONSE: Final[Route] = Route(
    POST, URI("/interactions/{interaction_id}/{interaction_token}/callback")
)
GET_ORIGINAL_INTERACTION_RESPONSE: Final[Route] = Route(
    GET, URI("/webhooks/{application_id}/{interaction_token}/messages/@original")
)
EDIT_ORIGINAL_INTERACTION_RESPONSE: Final[Route] = Route(
    PATCH, URI("/webhooks/{application_id}/{interaction_token}/messages/@original")
)
DELETE_ORIGINAL_INTERACTION_RESPONSE: Final[Route] = Route(
    DELETE, URI("/webhooks/{application_id}/{interaction_token}/messages/@original")
)
CREATE_APPLICATION_COMMAND: Final[Route] = Route("POST", URI("/applications/{application_id}/commands"))
CREATE_GUILD_APPLICATION_COMMAND: Final[Route] = Route(
    POST, URI("/applications/{application_id}/guilds/{guild_id}/commands")
)
GET_GUILD_APPLICATION_COMMANDS: Final[Route] = Route(
    GET, URI("/applications/{application_id}/guilds/{guild_id}/commands")
)

# Followups later

# Channels
GET_CHANNEL_MESSAGES: Final[Route] = Route(GET, URI("/channels/{channel_id}/messages"))

# User
GET_CURRENT_USER: Final[Route] = Route(GET, URI("/users/@me"))
GET_USER: Final[Route] = Route(GET, URI("/users/{user_id}"))
