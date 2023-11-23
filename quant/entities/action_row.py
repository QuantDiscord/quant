from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from quant.entities.interactions.component import Component


class ActionRow:
    """Container for components"""
    INTERACTION_TYPE: int = 1

    def __init__(self, components: List["Component"] | "Component") -> None:
        if isinstance(components, list):
            self.components = components
        else:
            self.components = [components]

    def as_json(self) -> Dict[str, Any]:
        return {
            "type": self.INTERACTION_TYPE,
            "components": [component.as_json() for component in self.components]
        }
