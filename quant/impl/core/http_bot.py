"""
MIT License

Copyright (c) 2024 MagM1go

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
import http
import warnings

from aiohttp import ClientSession, web

from quant.impl.core.route import GET, POST
from quant.impl.core.rest import RESTImpl
from quant.utils.asyncio_utils import kill_loop
from quant.utils.cache.cache_manager import CacheManager
from quant.utils.cache.cacheable import CacheableType
from quant.entities.interactions.interaction import InteractionType, InteractionCallbackType
from quant.entities.factory.event_factory import EventFactory
from quant.entities.factory.event_controller import EventController


class HTTPBot:
    """
    An interaction only bot implementation
    """
    def __init__(self, token: str, cacheable: CacheableType = CacheableType.ALL) -> None:
        warnings.warn("It's will be fully added in future. Now it's useless.")
        quit(1)

        self.cache = CacheManager()
        self.cache = CacheManager(cacheable=cacheable)
        self.rest = RESTImpl(token=token, cache=self.cache)
        self.event_factory = EventFactory(cache_manager=self.cache)
        self.event_controller = EventController(factory=self.event_factory)

        self.session = ClientSession()
        self._application = web.Application()

    async def _interaction_handler(self, request: web.Request) -> web.Response:
        if not request.method == POST:
            return web.Response(status=http.HTTPStatus.BAD_REQUEST)

        data: dict = await request.json()
        data_type = data.get("type")

        if data_type == InteractionType.PING.value:
            return web.json_response({"type": InteractionCallbackType.PONG})

        # okay it's future . . .

    def _setup_routes(self) -> None:
        self._application.add_routes([
            web.route(POST, "/interactions", self._interaction_handler)
        ])

    def run_server(self, host: str = "localhost", port: int = 8080) -> None:
        self._setup_routes()

        web.run_app(
            app=self._application,
            host=host,
            port=port
        )
