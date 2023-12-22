import asyncio

from quant.entities.intents import Intents
from .gateway import Gateway


class Shard:
    def __init__(self, num_shards: int, shard_id: int, intents: Intents = Intents.ALL_UNPRIVILEGED) -> None:
        self.shard_id = shard_id
        self.num_shards = num_shards
        self.gateway: Gateway | None = None
        self.intents = intents

    async def run(self, token: str) -> None:
        ...
    # pozor
