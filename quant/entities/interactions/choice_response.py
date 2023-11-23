from typing import List, Dict
from typing_extensions import Self

import attrs


@attrs.define(kw_only=True)
class ChoiceResponse:
    name: str = attrs.field()
    value: str = attrs.field(default=None)
    option_type: int = attrs.field(alias="type", converter=int)
    options: List[Self] | Dict = attrs.field(
        default=None,
        converter=lambda x: [ChoiceResponse(**i) for i in x] if x is not None else x
    )

    @classmethod
    def as_dict_iter(cls, data) -> List[Self] | None:
        if data is not None:
            return [cls(**choice) for choice in data]
