import json
from typing import Dict, Any

from aiohttp import ClientSession, ClientResponse

from quant.api.core.http_manager_abc import HttpManager
from quant.data.gateway.http_codes import HttpCodes
from quant.impl.core.exceptions.http_exception import Forbidden, InternalServerError
from quant.impl.core.exceptions.library_exception import DiscordException
from quant.impl.json_object import JSONObjectBuilder


class HttpManagerImpl(HttpManager):
    @staticmethod
    async def send_request(method: str, url: str,
                           data: Dict[str, Any] | JSONObjectBuilder = None,
                           headers: Dict[str, str] = None,
                           content_type: str = None) -> ClientResponse | None:
        async with ClientSession(headers=headers) as session:
            if headers is None:
                headers = {}

            if content_type is not None:
                headers.update({"Content-Type": content_type})
            if content_type is None:
                headers.update({"Content-Type": HttpManagerImpl.APPLICATION_JSON})

            if data is None:
                request = await session.request(method=method, url=url, headers=headers)
            else:
                if isinstance(data, JSONObjectBuilder):
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
            if 'code' in request_json_data.keys():
                raise DiscordException(request_text_data)

            match request.status:
                case HttpCodes.FORBIDDEN:
                    raise Forbidden("Not enough permissions")
                case HttpCodes.INTERNAL_SERVER_ERROR:
                    raise InternalServerError(f"Something went wrong on the server\n{request_text_data}")

            if request.ok or request_json_data['code'] != 50006:
                return request

            raise DiscordException(str(request_json_data))
