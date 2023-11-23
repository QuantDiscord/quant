import enum
from typing import Callable, Coroutine, Any, Dict

from quant.entities.interactions.component import Component
from .emoji import Emoji


class ButtonStyle(enum.Enum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class Button(Component):
    BUTTON_COMPONENT_TYPE: int = 2
    INTERACTION_TYPE: int = 3

    def __init__(
        self,
        custom_id: str | None,
        style: ButtonStyle = ButtonStyle.PRIMARY,
        label: str | None = None,
        emoji: Emoji | None = None,
        url: str | None = None,
        disabled: bool = False
    ) -> None:
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

        super().__init__(custom_id=custom_id)

    _Coroutine = Callable[..., Coroutine[Any, Any, Any]]

    def as_json(self) -> Dict[str, Any]:
        return {
            "type": self.BUTTON_COMPONENT_TYPE,
            "label": self.label,
            "custom_id": self.custom_id,
            "style": self.style.value,
            "emoji": self.emoji,
            "disabled": self.disabled,
            "url": self.url
        }
