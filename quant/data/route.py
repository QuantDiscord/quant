_G='/guilds/{guild_id}'
_F='/channels/{channel_id}/webhooks'
_E='/channels/{channel_id}/messages/{message_id}'
_D='/webhooks/{application_id}/{interaction_token}/messages/@original'
_C='DELETE'
_B='POST'
_A='GET'
from typing import Literal,Final,Any
import attrs
@attrs.define
class URI:
        _url_string:0;auto_format=True
        @property
        def url_string(self):
                A=self
                if not A.auto_format:return A._url_string
                return DISCORD_MAIN_API_URL+A._url_string
@attrs.define
class Route:method:0;uri:0;api_version=10
_ROUTE_FIELDS=attrs.fields(Route)
DISCORD_MAIN_API_URL='https://discord.com/api/v{}'.format(_ROUTE_FIELDS.api_version.default)
DISCORD_WS_URL=Route(_A,URI('wss://gateway.discord.gg/?v={}&encoding=json&compress=zlib-stream'.format(_ROUTE_FIELDS.api_version.default),auto_format=False))
GET_MESSAGE=Route(_A,URI(_E))
CREATE_MESSAGE=Route(_B,URI('/channels/{}/messages'))
DELETE_MESSAGE=Route(_C,URI(_E))
CREATE_REACTION=Route('PUT',URI('/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'))
GET_GUILD_EMOJI=Route(_A,URI('/guilds/{guild_id}/emojis/{emoji_id}'))
CREATE_WEBHOOK=Route(_B,URI(_F))
GET_CHANNEL_WEBHOOKS=Route(_A,URI(_F))
GET_GUILD=Route(_A,URI(_G))
CREATE_GUILD=Route(_B,URI('/guilds'))
DELETE_GUILD=Route(_C,URI(_G))
CREATE_INTERACTION_RESPONSE=Route(_B,URI('/interactions/{interaction_id}/{interaction_token}/callback'))
GET_ORIGINAL_INTERACTION_RESPONSE=Route(_A,URI(_D))
EDIT_ORIGINAL_INTERACTION_RESPONSE=Route('PATCH',URI(_D))
DELETE_ORIGINAL_INTERACTION_RESPONSE=Route(_C,URI(_D))
CREATE_APPLICATION_COMMAND=Route(_B,URI('/applications/{application_id}/commands'))
GET_CHANNEL_MESSAGES=Route(_A,URI('/channels/{channel_id}/messages'))