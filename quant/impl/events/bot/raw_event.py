from __future__ import annotations as _

from typing import Dict

import attrs

from quant.impl.events.event import InternalEvent


@attrs.define(kw_only=True)
class RawDispatchEvent(InternalEvent):
    data: Dict = attrs.field(default=None)

    def emit(self, *args, **kwargs):
        return self

    @staticmethod
    def build(event: RawDispatchEvent, *args, **kwargs) -> RawDispatchEvent:
        return event
