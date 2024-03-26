"""
MIT License

Copyright (c) 2023 MagM1go

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

import attrs


@attrs.define
class URI:
    _url_string: str
    auto_format: bool = True

    @property
    def url_string(self) -> str:
        if not self.auto_format:
            return self._url_string
        return Gateway.DISCORD_MAIN_API_URL + self._url_string


@attrs.define
class Route(attrs.AttrsInstance):
    method: str
    uri: URI
    api_version: int = 10


GET: Final[str] = "GET"
DELETE: Final[str] = "DELETE"
PATCH: Final[str] = "PATCH"
PUT: Final[str] = "PUT"
POST: Final[str] = "POST"

_ROUTE_FIELDS = attrs.fields(Route)


class Gateway:
    DISCORD_MAIN_API_URL: Final[str] = "https://discord.com/api/v{}".format(_ROUTE_FIELDS.api_version.default)
    DISCORD_WS_URL: Final[Route] = Route(
        "GET", URI(
            "wss://gateway.discord.gg/?v={}&encoding=json&compress=zlib-stream".format(_ROUTE_FIELDS.api_version.default),
            auto_format=False
        )
    )
    GATEWAY_BOT: Final[Route] = Route("GET", URI("/gateway/bot"))


class Message:
    GET_MESSAGE: Final[Route] = Route(GET, URI("/channels/{channel_id}/messages/{message_id}"))
    CREATE_MESSAGE: Final[Route] = Route(POST, URI("/channels/{channel_id}/messages"))
    EDIT_MESSAGE: Final[Route] = Route(PATCH, URI("/channels/{channel_id}/messages/{message_id}"))
    DELETE_MESSAGE: Final[Route] = Route(DELETE, URI("/channels/{channel_id}/messages/{message_id}"))
    CREATE_REACTION: Final[Route] = Route(PUT, URI("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"))
    GET_GUILD_EMOJI: Final[Route] = Route(GET, URI("/guilds/{guild_id}/emojis/{emoji_id}"))
    DELETE_ALL_REACTIONS: Final[Route] = Route(DELETE, URI("/channels/{channel_id}/messages/{message_id}/reactions"))
    DELETE_ALL_REACTION_FOR_EMOJI: Final[Route] = Route(
        DELETE, URI("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")
    )


class WebHook:
    CREATE_WEBHOOK: Final[Route] = Route(POST, URI("/channels/{channel_id}/webhooks"))
    GET_CHANNEL_WEBHOOKS: Final[Route] = Route(GET, URI("/channels/{channel_id}/webhooks"))
    CREATE_FOLLOWUP_MESSAGE: Final[Route] = Route(POST, URI("/webhooks/{application_id}/{interaction_token}"))


class Guild:
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


class Interaction:
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
    DELETE_GUILD_APPLICATION_COMMAND: Final[Route] = Route(
        GET, URI("/applications/{application_id}/guilds/{guild_id}/commands/{command_id}")
    )


class Channel:
    GET_CHANNEL_MESSAGES: Final[Route] = Route(GET, URI("/channels/{channel_id}/messages"))


class User:
    GET_CURRENT_USER: Final[Route] = Route(GET, URI("/users/@me"))
    GET_USER: Final[Route] = Route(GET, URI("/users/{user_id}"))
