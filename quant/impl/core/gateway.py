import sys
import enum
import time
import zlib
import logging
from typing import (
    Dict,
    NoReturn,
    List,
)
import asyncio
from traceback import print_exception

import json
import aiohttp

from quant.entities.activity import Activity
from quant.entities.snowflake import Snowflake
from quant.impl.core.route import DISCORD_WS_URL
from quant.entities.intents import Intents
from quant.entities.factory.event_factory import EventFactory
from quant.utils.cache.cache_manager import CacheManager
from quant.utils.asyncio_utils import get_loop


class OpCode(enum.IntEnum):
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


class Gateway:
    _ZLIB_SUFFIX = b'\x00\x00\xff\xff'

    def __init__(
        self,
        token: str,
        intents: Intents,
        api_version: int = 10,
        shard_id: int = 0,
        num_shards: int = 1
    ) -> None:
        self.token = token
        self.api_version = api_version
        self.websocket_connection: None | aiohttp.ClientWebSocketResponse = None
        self.ws_connected = False
        self.sequence = None
        self.session_id = None
        self._previous_heartbeat = 0
        self._mobile_status = False
        self.cache: CacheManager = CacheManager()
        self.event_factory = EventFactory(self)

        self.loop = get_loop()

        self.latency = None
        self.session = None

        self.raw_ws_request = {
            "token": self.token,
            "properties": {
                "os": sys.platform,
                "browser": "Discord iOS" if self._mobile_status else "quant",
                "device": "quant"
            },
            "shard": [shard_id, num_shards],
            "intents": intents.value,
            "large_threshold": 250
        }

        self.buffer = bytearray()
        self.zlib_decompressed_object = zlib.decompressobj()

        logging.basicConfig(format='%(levelname)s | %(asctime)s - %(message)s', level=logging.INFO)

    @property
    def identify_payload(self):
        return self.raw_ws_request

    @identify_payload.setter
    def identify_payload(self, data: Dict):
        self.raw_ws_request = data

    async def send_presence(self, activity: Activity = None, status: int = None, since: int = None, afk: bool = False):
        presence = {
            'activities': [
                {
                    'name': activity.name,
                    'type': activity.type,
                    'url': activity.url
                }
            ],
            'status': status,
            'since': since,
            'afk': afk
        }

        await self.send_data(self.create_payload(
            op=OpCode.PRESENCE_UPDATE,
            data=presence
        ))

    async def request_guild_members(
        self,
        guild_id: Snowflake,
        query: str = None,
        limit: int = None,
        presences: bool = False,
        user_ids: Snowflake | List[Snowflake] = None,
        nonce: bool = False
    ):
        payload = self.create_payload(
            op=OpCode.REQUEST_GUILD_MEMBERS,
            data={
                'guild_id': guild_id,
                'query': query,
                'limit': limit,
                'presences': presences,
                'user_ids': user_ids,
                'nonce': nonce
            }
        )
        await self.send_data(payload)

    @property
    def get_logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    async def connect_ws(self) -> None:
        self.session = aiohttp.ClientSession()
        self.websocket_connection = await self.session.ws_connect(
            DISCORD_WS_URL.uri.url_string.format(self.api_version)
        )

        self.ws_connected = True

        self.zlib_decompressed_object = zlib.decompressobj()
        self.buffer = bytearray()

        self.get_logger.info("WebSocket connected")
        await self.send_identify()
        self.loop.create_task(self.read_websocket())
        await self.keep_alive_check()

    async def error_reconnect(self, code: int):
        self.get_logger.info("Reconnecting")

        if code == 4009:
            return await self.resume_connection()

        self.ws_connected = False
        await self.connect_ws()

    async def on_websocket_message(self, received_data):
        if isinstance(received_data, bytes):
            self.buffer.extend(received_data)

            if len(received_data) < 4 or received_data[-4:] != self._ZLIB_SUFFIX:
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

        match OpCode(op):
            case OpCode.DISPATCH:
                self.sequence = int(sequence)
                received_event_type = received_data["t"]

                self.cache.add_from_event(received_event_type, **received_data["d"])
                event = self.event_factory.build_event(received_event_type, **received_data["d"])
                await self.event_factory.dispatch(event)
            case OpCode.INVALID_SESSION:
                await self.websocket_connection.close(code=4000)
                await self.error_reconnect(code=4000)
            case OpCode.HELLO:
                await self.send_hello(received_data)
            case OpCode.HEARTBEAT_ACK:
                self.latency = time.perf_counter() - self._previous_heartbeat
            case OpCode.RECONNECT:
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
                self.get_logger.error("Gateway received close code: %s", close_code)
                break

    async def send_data(self, data) -> None:
        await self.websocket_connection.send_str(data)

    async def resume_connection(self):
        self.get_logger.info("Connection resumed")

        if self.websocket_connection.closed:
            return

        payload = self.create_payload(OpCode.RESUME, {
            "token": self.token,
            "session_id": self.session_id,
            "seq": self.sequence
        })
        await self.send_data(payload)

    async def send_identify(self, resume: bool = False) -> None:
        if resume:
            return await self.resume_connection()

        await self.send_data(self.create_payload(OpCode.IDENTIFY, self.identify_payload))
        self.get_logger.info("Bot identified")

    async def close(self, code: int = 4000):
        self.get_logger.info("Connection closing, code: %s", code)

        if not self.websocket_connection:
            return

        self.ws_connected = False
        await self.websocket_connection.close(code=code)

        self.buffer.clear()

    async def send_heartbeat(self, interval: float):
        if self.websocket_connection.closed:
            return

        await self.send_data(self.create_payload(OpCode.HEARTBEAT, sequence=self.sequence))
        self._previous_heartbeat = time.perf_counter()

        await asyncio.sleep(interval)
        self.loop.create_task(self.send_heartbeat(interval))

    async def send_hello(self, data: Dict) -> None:
        self.get_logger.info("Hello sent")
        interval = data["d"]["heartbeat_interval"] / 1000
        await asyncio.sleep((interval - 2000) / 1000)

        self.loop.create_task(self.send_heartbeat(interval))

    async def connect_voice(
        self,
        guild_id: int,
        channel_id: int = None,
        self_mute: bool = False,
        self_deaf: bool = False
    ) -> None:
        payload = self.create_payload(
            op=OpCode.VOICE_STATE_UPDATE,
            data={
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": self_mute,
                "self_deaf": self_deaf
            }
        )
        await self.send_data(payload)

    @staticmethod
    def create_payload(
        op: OpCode,
        data=None, sequence: int = None,
        event_name: str = None
    ) -> str:
        payload = {"op": op, "d": data}
        if op == OpCode.DISPATCH:
            payload.update({"s": sequence, "t": event_name})

        return json.dumps(payload)

    @property
    def mobile_status(self) -> bool:
        return self._mobile_status

    @mobile_status.setter
    def mobile_status(self, value: bool):
        self._mobile_status = value

    @staticmethod
    def create_new_loop() -> asyncio.AbstractEventLoop:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        return loop
