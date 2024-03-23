import asyncio
import json
import http
from typing import Dict, Any, TypeVar
from datetime import datetime

from aiohttp import ClientSession, ClientResponse, FormData

from quant.api.core.http_manager_abc import HttpManager, AcceptContentType
from quant.entities.ratelimits.ratelimit import RateLimit
from quant.impl.core.exceptions.http_exception import Forbidden, InternalServerError, HTTPException
from quant.utils.parser import timestamp_to_datetime
from quant.utils import logger

DataT = TypeVar("DataT", bound=Dict[str, Any] | FormData)
HeadersT = TypeVar("HeadersT", bound=Dict[str, Any] | None)


class HttpManagerImpl(HttpManager):
    def __init__(self, authorization: str | None = None) -> None:
        self.authorization = authorization
        self.max_retries = 3

    async def parse_ratelimits(self, response: ClientResponse) -> RateLimit | None:
        if response.status != http.HTTPStatus.TOO_MANY_REQUESTS:
            return

        if response.content_type != AcceptContentType.APPLICATION_JSON:
            return

        headers = response.headers
        if headers is None:
            return

        if (max_retries := headers.get("X-RateLimit-Limit")) is not None:
            self.max_retries = int(max_retries)

        remaining_retries, ratelimit_reset = (
            headers.get("X-RateLimit-Remaining"),
            headers.get("X-RateLimit-Reset")
        )

        if ratelimit_reset is None:
            return

        ratelimit_reset = timestamp_to_datetime(int(ratelimit_reset[:-4]))
        if ratelimit_reset <= datetime.now():
            return

        response_data: Dict = await response.json()
        retry_after, message, is_global, code = (
            response_data.get("retry_after"),
            response_data.get("message"),
            response_data.get("global"),
            response_data.get("code")
        )

        return RateLimit(
            max_retries=self.max_retries,
            remaining_retries=int(remaining_retries),
            ratelimit_reset=ratelimit_reset,
            retry_after=retry_after,
            message=message,
            is_global=is_global,
            code=code
        )

    def _build_base_headers(self, headers: DataT = None) -> Dict:
        if headers is None:
            headers = {}

        header_keys = {"Authorization": self.authorization, "Content-Type": AcceptContentType.APPLICATION_JSON}

        for key, value in header_keys.items():
            if headers.get(key) is None:
                headers[key] = value

        return headers

    async def request(
        self,
        method: str, url: str,
        data: DataT = None,
        headers: HeadersT = None,
        pre_build_headers: bool = True,
        form_data: FormData | None = None
    ) -> ClientResponse | None:
        if data is not None and form_data is not None:
            raise HTTPException("Can't handle form data and data at same time")

        if pre_build_headers:
            headers = self._build_base_headers(headers)

        async with ClientSession(headers=headers) as session:
            request_data = {
                "method": method,
                "url": url,
                "headers": headers
            }

            async def perform_request() -> ClientResponse:
                if data is not None:
                    request_data["data"] = json.dumps(data)

                if form_data is not None:
                    request_data["data"] = form_data

                return await session.request(**request_data)

            response = await perform_request()
            if not response.ok:
                match response.status:
                    case http.HTTPStatus.TOO_MANY_REQUESTS:
                        ratelimits = await self.parse_ratelimits(response)
                        for i in range(ratelimits.max_retries):
                            logger.warn(f"You're being rate limited, retrying (attempt: {i + 1}, retry time: {ratelimits.retry_after})")
                            response = await perform_request()

                            if response.ok:
                                return response

                            await asyncio.sleep(ratelimits.retry_after)
                        return response
                    case http.HTTPStatus.NO_CONTENT:
                        return
                    case http.HTTPStatus.FORBIDDEN:
                        raise Forbidden("Missing permissions")
                    case http.HTTPStatus.INTERNAL_SERVER_ERROR:
                        raise InternalServerError("Server issue, try again")

                if response.status not in (http.HTTPStatus.TOO_MANY_REQUESTS, http.HTTPStatus.TOO_MANY_REQUESTS):
                    raise HTTPException(
                        f"Request corrupted or invalid request body. More data below\nResponse: {await response.read()}\n"
                        f"Method: {method}\n"
                        f"URL: {response.url}\n"
                        f"Data: {data}\n"
                    )

            return response
