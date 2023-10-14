from __future__ import annotations

from typing import List

import attrs


@attrs.define(kw_only=True)
class ChoiceResponse:
    name: str = attrs.field()
    value: str = attrs.field()
    option_type: int = attrs.field(alias="type", converter=int)

    @classmethod
    def as_dict_iter(cls, data) -> List[ChoiceResponse] | None:
        if data is not None:
            return [cls(**choice) for choice in data]
