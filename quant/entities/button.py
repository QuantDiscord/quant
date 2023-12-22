import enum
from typing import Callable, Coroutine, Any, Dict

from quant.entities.interactions.component import Component
from .emoji import Emoji
from quant.impl.core.context import ButtonContext


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
        self._disabled = disabled

        super().__init__(custom_id=custom_id)

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._disabled = value

    _Coroutine = Callable[..., Coroutine[Any, Any, Any]]

    async def callback(self, context: ButtonContext):
        pass

    callback_func = callback

    def set_callback(self, coro):
        self.callback_func = coro

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
