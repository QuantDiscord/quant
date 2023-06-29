import json
from typing import Dict, Any

from aiohttp import ClientSession, ClientResponse

from dispy.data.gateway import HttpCodes
from dispy.impl.core.exceptions.http_exception import Forbidden
from dispy.impl.core.exceptions.library_exception import LibraryException


class HttpManager:
    APPLICATION_JSON = "application/json"
    MULTIPART_FORM_DATA = "multipart/form-data"
    AUTHORIZATION = "Authorization"

    @staticmethod
    async def send_request(method: str, url: str,
                           data: Dict[str, Any] = None,
                           headers: Dict[str, str] = None) -> ClientResponse | None:
        async with ClientSession(headers=headers) as session:
            request = await session.request(method=method, url=url, data=json.dumps(data), headers=headers)
            request_text_data = await request.text()

            if request_text_data == "":
                return

            request_json_data = await request.json()

            match request.status:
                case HttpCodes.FORBIDDEN:
                    raise Forbidden("Not enough permissions")

            if request.ok or request_json_data['code'] != 50006:
                return request

            raise LibraryException(str(request_json_data))
