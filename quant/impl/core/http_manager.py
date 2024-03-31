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
import asyncio
import http
import json
from typing import Dict, Any, TypeVar
from datetime import datetime

from aiohttp import ClientSession, ClientResponse, FormData

from quant.utils import logger, parser
from quant.api.core.http_manager_abc import HttpManager, AcceptContentType
from quant.entities.ratelimits.ratelimit import RateLimit, RateLimitBucketReset, Bucket
from quant.impl.core.exceptions.http_exception import Forbidden, InternalServerError, HTTPException

DataT = TypeVar("DataT", bound=Dict[str, Any] | FormData | list)
HeadersT = TypeVar("HeadersT", bound=Dict[str, Any] | None)


class HttpManagerImpl(HttpManager):
    def __init__(self, authorization: str | None = None) -> None:
        self.authorization = authorization
        self.max_retries = 3
        self.session = ClientSession()

    async def parse_ratelimits(self, response: ClientResponse) -> Bucket | None:
        if response.status != http.HTTPStatus.TOO_MANY_REQUESTS:
            return

        if response.content_type != AcceptContentType.APPLICATION_JSON:
            return

        headers = response.headers
        if headers is None:
            return

        if (max_retries := headers.get("X-RateLimit-Limit")) is not None:
            self.max_retries = int(max_retries)

        remaining_retries, ratelimit_reset, reset_after, scope, bucket = (
            headers.get("X-RateLimit-Remaining"),
            headers.get("X-RateLimit-Reset"),
            headers.get("X-RateLimit-Reset-After"),
            headers.get("x-RateLimit-Scope"),
            headers.get("X-RateLimit-Bucket")
        )

        time = parser.timestamp_to_datetime(int(ratelimit_reset[:-4]))
        bucket_reset_time = RateLimitBucketReset(
            reset_time=time,
            reset_time_milliseconds=float(reset_after)
        )
        if bucket_reset_time.reset_time <= datetime.now() or bucket_reset_time.reset_time_milliseconds <= 0:
            return Bucket(
                rate_limit=None,
                bucket_reset=bucket_reset_time
            )

        response_data: Dict = await response.json()
        retry_after, message, is_global, code = (
            response_data.get("retry_after"),
            response_data.get("message"),
            response_data.get("global"),
            response_data.get("code")
        )

        ratelimit = RateLimit(
            max_retries=self.max_retries,
            remaining_retries=int(remaining_retries),
            retry_after=retry_after,
            message=message,
            is_global=is_global,
            code=code,
            scope=scope,
            bucket=bucket
        )
        return Bucket(
            rate_limit=ratelimit,
            bucket_reset=bucket_reset_time
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

        request_data = {
            "method": method,
            "url": url
        }

        if headers is not None:
            request_data["headers"] = headers

        async def perform_request() -> ClientResponse:
            if data is not None:
                request_data["data"] = json.dumps(data)

            if form_data is not None:
                request_data["data"] = form_data

            return await self.session.request(**request_data)

        response = await perform_request()
        if response.ok:
            return response

        match response.status:
            case http.HTTPStatus.TOO_MANY_REQUESTS:
                ratelimits_bucket = await self.parse_ratelimits(response)
                ratelimit = ratelimits_bucket.rate_limit
                for i in range(ratelimit.max_retries):
                    logger.warn(
                        f"You're being rate limited, retrying "
                        f"(attempt: {i + 1}, retry time: {ratelimit.retry_after}, scope: {ratelimit.scope})"
                    )
                    response = await perform_request()
                    if response.ok:
                        return response
                    await asyncio.sleep(ratelimit.retry_after)
                return response
            case http.HTTPStatus.FORBIDDEN:
                raise Forbidden("Missing permissions")
            case http.HTTPStatus.INTERNAL_SERVER_ERROR:
                raise InternalServerError("Server issue, try again")
            case http.HTTPStatus.NO_CONTENT:
                return

        if response.status not in (
            http.HTTPStatus.TOO_MANY_REQUESTS,
            http.HTTPStatus.NO_CONTENT
        ):
            raise HTTPException(
                f"Request corrupted or invalid request body. More data below\n"
                f"Response: {await response.read()}\n"
                f"Method: {method}\n"
                f"URL: {response.url}\n"
                f"Data: {data}\n"
            )
