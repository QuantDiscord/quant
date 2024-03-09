from __future__ import annotations as _

from typing import List, TypeVar

from quant.entities.button import Button

ComponentT = TypeVar("ComponentT", bound=Button)


class ActionRow:
    """Container for components

    Parameters
    ==========
    components: :class:`List[ComponentT] | ComponentT`
        Action row components
    """
    INTERACTION_TYPE = 1

    def __init__(self, components: List[ComponentT] | ComponentT) -> None:
        if isinstance(components, list):
            self.components = components
        else:
            self.components = [components]
