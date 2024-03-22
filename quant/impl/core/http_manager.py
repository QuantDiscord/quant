import asyncio
import json
from typing import Dict, Any, TypeVar

from aiohttp import ClientSession, ClientResponse, FormData

from quant.api.core.http_manager_abc import HttpManager, AcceptContentType
from quant.entities.http_codes import HttpCodes
from quant.impl.core.exceptions.http_exception import Forbidden, InternalServerError, RateLimitExceeded
from quant.impl.core.exceptions.library_exception import DiscordException
from quant.utils.json_builder import MutableJsonBuilder

DataT = TypeVar("DataT", bound=Dict[str, Any] | MutableJsonBuilder[str, Any] | FormData)


class HttpManagerImpl(HttpManager):
    def __init__(self, authorization: str | None = None, max_retries: int = 3) -> None:
        self.authorization = authorization
        self.max_retries = max_retries

    async def _perform_json_request(
        self,
        method: str,
        url: str,
        data: MutableJsonBuilder[str, Any] = None,
        headers: MutableJsonBuilder[str, Any] = None,
        content_type: str = None
    ) -> ClientResponse | None:
        if headers is None:
            headers = MutableJsonBuilder()
        else:
            headers = MutableJsonBuilder(headers.asdict())

        async with ClientSession() as session:
            if self.authorization is not None:
                headers.put("Authorization", self.authorization)

            if content_type is not None:
                headers.put("Content-Type", content_type)

            if content_type is None:
                headers.put("Content-Type", AcceptContentType.APPLICATION_JSON)

            headers = headers.asdict()
            if data is None or len(data.asdict()) == 0:
                request = await session.request(method=method, url=url, headers=headers)
            else:
                request = await session.request(method=method, url=url, data=json.dumps(data.asdict()), headers=headers)

            return await self._validate_request(request=request)

    async def _perform_dict_request(
        self,
        method: str,
        url: str,
        data: Dict[str, Any] = None,
        headers: Dict[str, Any] | None = None,
        content_type: str = None
    ) -> ClientResponse | None:
        if headers is None:
            headers = {}

        async with ClientSession() as session:
            if self.authorization is not None:
                headers.update({"Authorization": self.authorization})

            if content_type is not None:
                headers.update({"Content-Type": content_type})

            if content_type is None:
                headers.update({"Content-Type": AcceptContentType.APPLICATION_JSON})

            if data is None:
                request = await session.request(method=method, url=url, headers=headers)
            else:
                if not isinstance(data, FormData):
                    data = json.dumps(data)

                request = await session.request(method=method, url=url, data=data, headers=headers)

            return await self._validate_request(request=request)

    @staticmethod
    async def _validate_request(request: ClientResponse) -> ClientResponse | None:
        content_type = request.content_type
        request_text_data = await request.read()
        if request_text_data == "":
            return

        mimetypes = (
            AcceptContentType.MimeTypes.IMAGE_PNG,
            AcceptContentType.MimeTypes.IMAGE_GIF,
            AcceptContentType.MimeTypes.IMAGE_JPG,
            AcceptContentType.MimeTypes.IMAGE_WEBP
        )
        if content_type in mimetypes:
            return request

        if content_type == AcceptContentType.TEXT_HTML:
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
            case HttpCodes.TOO_MANY_REQUESTS:
                raise RateLimitExceeded(f"You're being ratelimited, retry after {request_json_data['retry_after']}")

        if request.ok or request_json_data['code'] != 50006:
            return request

        raise DiscordException(str(request_json_data))

    async def send_request(
        self,
        method: str,
        url: str,
        data: DataT = None,
        headers: Dict[str, str] | MutableJsonBuilder[str, Any] | None = None,
        content_type: str = None
    ) -> ClientResponse | None:
        retry_attempts = 0

        while retry_attempts < self.max_retries:
            response = await self._send_performed_request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                content_type=content_type
            )

            if response is None:
                return

            if response.ok:
                return response

            if response.status == HttpCodes.BAD_REQUEST:
                raise DiscordException("Illegal or bad request (probably library issue)")

            retry_attempts += 1
            await asyncio.sleep(2 ** retry_attempts)

        raise RateLimitExceeded("Failed ratelimit request")

    async def _send_performed_request(
        self,
        method: str,
        url: str,
        data: DataT = None,
        headers: Dict[str, str] | MutableJsonBuilder[str, Any] | None = None,
        content_type: str = None
    ) -> ClientResponse | None:
        if isinstance(data, MutableJsonBuilder) or isinstance(headers, MutableJsonBuilder):
            response = await self._perform_json_request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                content_type=content_type
            )
        else:
            response = await self._perform_dict_request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                content_type=content_type
            )

        return response
