from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant.impl.core.client import Client

from quant.impl.events.bot.ready_event import ShardReadyEvent
from quant.entities.activity import ActivityData
from quant.entities.intents import Intents
from .gateway import Gateway


class Shard:
    def __init__(self, num_shards: int, shard_id: int, intents: Intents = Intents.ALL_UNPRIVILEGED) -> None:
        self.shard_id = shard_id
        self.num_shards = num_shards
        self.gateway: Gateway | None = None
        self.intents = intents

    async def start(self, client: Client, loop: asyncio.AbstractEventLoop = None) -> None:
        self.gateway = Gateway(
            intents=self.intents,
            shard_id=self.shard_id,
            num_shards=self.num_shards,
            client=client
        )

        if loop is not None:
            client.loop = loop

        client.shards.append(self)

        asyncio.create_task(self.gateway.start())

        event = ShardReadyEvent()
        event.shard_id = self.shard_id
        await client.event_controller.dispatch(event)
        await asyncio.sleep(5)

    async def close(self) -> None:
        asyncio.create_task(self.gateway.close())

    async def send_presence(self, activity: ActivityData):
        await self.gateway.send_presence(
            activity=activity.activity,
            status=activity.status,
            since=activity.since,
            afk=activity.afk
        )
