from typing import Dict, Any, List, Tuple

from quant.data.components.component import Component


class ActionRow:
    """Container for components"""
    INTERACTION_TYPE: int = 1

    def __init__(self, *components: Component) -> None:
        self.components = components

    def as_json(self) -> Dict[str, Any]:
        return {
            "type": self.INTERACTION_TYPE,
            "components": [component.as_json() for component in self.components]
        }

    def as_dict_iter(self) -> tuple[Component, ...]:
        if self is not None:
            return self.components
