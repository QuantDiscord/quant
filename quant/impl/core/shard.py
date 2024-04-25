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
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant.impl.core.client import Client

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

        self._latency: float = float("nan")

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

    @property
    def latency(self) -> float:
        return self._latency

    @latency.setter
    def latency(self, value: float) -> None:
        self._latency = value
