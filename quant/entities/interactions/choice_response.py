from typing import List, Dict
from typing_extensions import Self

import attrs

from .slash_option import SlashOptionType


@attrs.define(kw_only=True)
class InteractionDataOption:
    name: str = attrs.field()
    value: str = attrs.field()
    type: SlashOptionType = attrs.field()
    options: List[Self] | Dict = attrs.field()
    focused: bool = attrs.field()
