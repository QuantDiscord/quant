from typing import Callable, Coroutine, Any, Dict

from quant.components.component import Component
from quant.data.guild.messages.emoji import Emoji
from quant.components.buttons.button_style import ButtonStyle
from quant.data.guild.messages.interactions.interaction import Interaction


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

    async def callback(self, interaction: Interaction) -> None:
        ...

    callback_func = callback

    def set_callback(self, coro: _Coroutine) -> None:
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
