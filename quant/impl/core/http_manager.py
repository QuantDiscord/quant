import json
from typing import Dict, Any

from aiohttp import ClientSession, ClientResponse

from quant.api.core.http_manager_abc import HttpManager
from quant.entities.http_codes import HttpCodes
from quant.impl.core.exceptions.http_exception import Forbidden, InternalServerError
from quant.impl.core.exceptions.library_exception import DiscordException
from quant.utils.json_builder import MutableJsonBuilder


class HttpManagerImpl(HttpManager):
    def __init__(self, authorization: str | None = None) -> None:
        self.authorization = authorization

    async def send_request(
        self,
        method: str, url: str,
        data: Dict[str, Any] | MutableJsonBuilder[str, Any] = None,
        headers: Dict[str, str] | MutableJsonBuilder[str, Any] | None = None,
        content_type: str = None
    ) -> ClientResponse | None:
        async with ClientSession(
            headers=headers if not isinstance(headers, MutableJsonBuilder) else headers.asdict()
        ) as session:
            if headers is None or len(headers) == 0:
                headers = MutableJsonBuilder()
            else:
                headers = MutableJsonBuilder(headers)

            if self.authorization is not None:
                headers.put("Authorization", self.authorization)

            if content_type is not None:
                headers.put("Content-Type", content_type)

            if content_type is None:
                headers.put("Content-Type", HttpManagerImpl.APPLICATION_JSON)

            headers = headers.asdict()
            if data is None:
                request = await session.request(method=method, url=url, headers=headers)
            else:
                if isinstance(data, MutableJsonBuilder):
                    data = data.asdict()
                else:
                    data = data

                request = await session.request(method=method, url=url, data=json.dumps(data), headers=headers)

            content_type = request.content_type
            request_text_data = await request.text()
            if request_text_data == "":
                return

            if content_type == HttpManagerImpl.TEXT_HTML:
                return request

            request_json_data = await request.json()
            if isinstance(request_json_data, list):
                return request

            if isinstance(request_json_data, dict) and 'code' in request_json_data.keys():
                raise DiscordException(request_text_data)

            match request.status:
                case HttpCodes.FORBIDDEN:
                    raise Forbidden("Not enough permissions")
                case HttpCodes.INTERNAL_SERVER_ERROR:
                    raise InternalServerError(f"Something went wrong on the server\n{request_text_data}")

            if request.ok or request_json_data['code'] != 50006:
                return request

            raise DiscordException(str(request_json_data))
