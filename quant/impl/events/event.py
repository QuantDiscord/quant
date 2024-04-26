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
from __future__ import annotations as _

from typing import TypeVar, TYPE_CHECKING
from abc import ABC, abstractmethod

import attrs

if TYPE_CHECKING:
    from typing_extensions import Self

from quant.impl.events.types import EventTypes
from quant.entities.factory.entity_factory import EntityFactory
from quant.utils.cache.cache_manager import CacheManager


class Event:
    async def call(self) -> None:
        ...

    def emit(self, *args, **kwargs) -> Self:
        ...


class InternalEvent(ABC, Event):
    T = TypeVar("T")

    @staticmethod
    @abstractmethod
    def build(event: T, *args, **kwargs) -> T:
        ...


@attrs.define
class DiscordEvent(Event):
    event_api_name: EventTypes = attrs.field()
    cache_manager: CacheManager = attrs.field()
    entity_factory: EntityFactory = attrs.field()
