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

from typing import Dict

import attrs

from quant.impl.events.event import InternalEvent


@attrs.define(kw_only=True)
class _GatewayData:
    event_name: str = attrs.field(alias="t")
    sequence: int = attrs.field(alias="s")
    opcode: int = attrs.field(alias="op")
    data: Dict = attrs.field(alias="d")


@attrs.define(kw_only=True)
class RawDispatchEvent(InternalEvent):
    data: _GatewayData = attrs.field()

    def emit(self, *args, **kwargs):
        return self

    @staticmethod
    def build(event: RawDispatchEvent, *args, **kwargs) -> RawDispatchEvent:
        return event
