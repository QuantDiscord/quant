import sys
import time
import zlib
import logging
from typing import (
    Dict,
    Callable,
    List,
    NoReturn
)

import json
import aiohttp
import asyncio
from traceback import print_exception

from dispy.data.activities.activity import Activity
from dispy.data.route import DISCORD_WS_URL
from dispy.data.intents import Intents
from dispy.impl.events.dispatch import dispatch
from dispy.impl.events.event import BaseEvent
from dispy.utils.cache_manager import CacheManager


class Gateway:
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11

    ZLIB_SUFFIX = b'\x00\x00\xff\xff'

    def __init__(
        self,
        token: str,
        intents: Intents,
        mobile_status: bool = False,
        api_version: int = 10
    ) -> None:
        self.token = token
        self.api_version = api_version
        self.websocket_connection: None | aiohttp.ClientWebSocketResponse = None
        self.ws_connected = False
        self.sequence = None
        self.session_id = None
        self._previous_heartbeat = 0
        self.mobile_status = mobile_status
        self._events: Dict[Callable, Dict[str, BaseEvent]] = {}
        self.cache = CacheManager()

        self.loop = asyncio.get_event_loop()

        self.latency = None
        self.session = None

        self.raw_ws_request = {
            "token": self.token,
            "properties": {
                "os": sys.platform,
                "browser": "Discord Android" if self.mobile_status else "dispy",
                "device": "dispy"
            },
            "intents": intents.value
        }

        self.buffer = bytearray()
        self.zlib_decompressed_object = zlib.decompressobj()

        logging.basicConfig(format='%(asctime)s %(message)s')

        self.logger = logging.getLogger(name="DsPy")

    async def connect_ws(self) -> None:
        self.session = aiohttp.ClientSession()
        self.websocket_connection = await self.session.ws_connect(DISCORD_WS_URL.uri.url_string.format(self.api_version))

        self.ws_connected = True

        self.zlib_decompressed_object = zlib.decompressobj()
        self.buffer = bytearray()

        await self.send_identify()
        self.loop.create_task(self.read_websocket())
        await self.keep_alive_check()

    async def error_reconnect(self, code: int):
        if code == 4009:
            await self.resume_connection()
            return

        self.ws_connected = False
        await self.connect_ws()

    async def on_websocket_message(self, received_data):
        if isinstance(received_data, bytes):
            self.buffer.extend(received_data)

            if len(received_data) < 4 or received_data[-4:] != self.ZLIB_SUFFIX:
                return

            received_data = self.zlib_decompressed_object.decompress(self.buffer)
            try:
                received_data = received_data.decode("utf8")
                self.buffer = bytearray()
            except zlib.error:
                return

        received_data = json.loads(received_data)
        op = received_data["op"]
        sequence = received_data["s"]

        match op:
            case self.DISPATCH:
                self.sequence = int(sequence)
                received_event_type = received_data["t"]

                self.cache.cache_register(received_event_type, **received_data["d"])
                await dispatch(self, received_event_type, **received_data["d"])
            case self.INVALID_SESSION:
                await self.websocket_connection.close(code=4000)
                await self.error_reconnect(code=4000)
            case self.HELLO:
                await self.send_hello(received_data)
            case self.HEARTBEAT_ACK:
                self.latency = time.perf_counter() - self._previous_heartbeat
            case self.RECONNECT:
                await self.close(code=1012)

    async def keep_alive_check(self) -> None:
        while self.ws_connected:
            await asyncio.sleep(20)

            one_minute = float(60)

            if (self._previous_heartbeat + one_minute) < time.perf_counter():
                await self.websocket_connection.close(code=4000)
                await self.error_reconnect(code=4000)

    async def read_websocket(self) -> NoReturn:
        while self.ws_connected:
            async for message in self.websocket_connection:
                match message.type:
                    case aiohttp.WSMsgType.BINARY | aiohttp.WSMsgType.TEXT:
                        try:
                            await self.on_websocket_message(message.data)
                        except Exception as exception:
                            print_exception(exception)
                    case _:
                        raise RuntimeError

            close_code = self.websocket_connection.close_code
            if close_code is not None:
                ...

    async def send_data(self, data) -> None:
        await self.websocket_connection.send_str(data)

    async def resume_connection(self):
        if self.websocket_connection.closed:
            return

        payload = self.create_payload(self.RESUME, {
            "token": self.token,
            "session_id": self.session_id,
            "seq": self.sequence
        })
        await self.send_data(payload)

    async def send_identify(self, resume: bool = False) -> None:
        if resume:
            return await self.resume_connection()

        await self.send_data(self.create_payload(self.IDENTIFY, self.raw_ws_request))

    async def close(self, code: int = 4000):
        if not self.websocket_connection:
            return

        self.ws_connected = False
        await self.websocket_connection.close(code=code)

        self.buffer.clear()

    async def send_heartbeat(self, interval: float):
        if self.websocket_connection.closed:
            return

        await self.send_data(self.create_payload(self.HEARTBEAT, sequence=self.sequence))
        self._previous_heartbeat = time.perf_counter()

        await asyncio.sleep(interval)
        self.loop.create_task(self.send_heartbeat(interval))

    async def send_hello(self, data: Dict) -> None:
        interval = data["d"]["heartbeat_interval"] / 1000
        await asyncio.sleep((interval - 2000) / 1000)

        self.loop.create_task(self.send_heartbeat(interval))

    def create_payload(
        self, op: int,
        data=None, sequence: int = None,
        event_name: str = None
    ) -> str:
        payload = {}

        payload.update({"op": op, "d": data})

        if op == self.DISPATCH:
            payload.update({"s": sequence, "t": event_name})

        return json.dumps(payload)

    def set_presence(
        self,
        activity: Activity = None,
        status: str = None,
        since: int = None,
        afk: bool = None
    ):
        self.raw_ws_request["presence"] = dict(
            activities=[{
                "name": activity.name,
                "type": activity.type.value,
                "url": activity.url
            }],
            status=status,
            since=since,
            afk=afk
        )

    def add_event(self, event_name, event_type, event_callback) -> None:
        self._events[event_callback] = {event_name: event_type}

    def event_list(self) -> Dict[Callable, Dict[str, BaseEvent]]:
        return self._events
