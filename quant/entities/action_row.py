from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from quant.api.entities.component import Component


class ActionRow:
    """Container for components"""
    INTERACTION_TYPE: int = 1

    def __init__(self, components: List["Component"] | "Component") -> None:
        if isinstance(components, list):
            self.components = components
        else:
            self.components = [components]
