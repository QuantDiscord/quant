from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant.impl.core.client import Client

from quant.impl.events.bot.ready_event import ShardReadyEvent
from quant.entities.intents import Intents
from quant.entities.activity import Activity
from .gateway import Gateway


class Shard:
    def __init__(
        self,
        num_shards: int,
        shard_id: int,
        intents: Intents = Intents.ALL_UNPRIVILEGED,
        mobile: bool = False,
        activity: Activity | None = None
    ) -> None:
        self.shard_id = shard_id
        self.num_shards = num_shards
        self.gateway: Gateway | None = None
        self.intents = intents
        self.mobile = mobile
        self.activity = activity

    async def start(self, client: Client, loop: asyncio.AbstractEventLoop = None) -> None:
        self.gateway = Gateway(
            intents=self.intents,
            shard_id=self.shard_id,
            num_shards=self.num_shards,
            client=client,
            mobile=self.mobile
        )

        if loop is not None:
            client.loop = loop

        asyncio.create_task(self.gateway.connect())

        if self.shard_id == 0:
            client.gateway = self.gateway

    async def close(self) -> None:
        asyncio.create_task(self.gateway.close())
