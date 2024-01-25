import asyncio

import aiohttp
from typing_extensions import Self

from quant.impl.events.bot.ready_event import ShardReadyEvent
from quant.entities.intents import Intents
from .gateway import Gateway


class Shard:
    def __init__(self, num_shards: int, shard_id: int, intents: Intents = Intents.ALL_UNPRIVILEGED) -> None:
        self.shard_id = shard_id
        self.num_shards = num_shards
        self.gateway: Gateway | None = None
        self.intents = intents

    async def start(self, token: str) -> Self:
        self.gateway = Gateway(
            token=token,
            intents=self.intents,
            shard_id=self.shard_id,
            num_shards=self.num_shards
        )

        asyncio.create_task(self.gateway.start())

        event = ShardReadyEvent()
        event.shard_id = self.shard_id
        await self.gateway.event_controller.dispatch(event)
        return self

    async def close(self) -> None:
        asyncio.create_task(self.gateway.close())
