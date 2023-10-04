from typing import Callable, Coroutine, Any, Dict

from dispy.components.component import Component
from dispy.data.guild.messages.emoji import Emoji
from dispy.components.buttons.button_style import ButtonStyle
from dispy.impl.events.bot.interaction_create_event import InteractionCreateEvent
from dispy.data.guild.messages.interactions.interaction import Interaction


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

        self.client.add_listener(InteractionCreateEvent, self.on_button_click)

        super().__init__(custom_id=custom_id)

    _Coroutine = Callable[..., Coroutine[Any, Any, Any]]

    async def on_button_click(self, event: InteractionCreateEvent):
        if not event.interaction.interaction_type == Button.INTERACTION_TYPE:
            return

        channel_id = event.interaction.channel_id
        message_id = event.interaction.message.message_id
        message = await event.interaction.client.rest.fetch_message(channel_id, message_id)

        for component in message.components:
            custom_id = component["components"][0]["custom_id"]
            if custom_id == self.custom_id:
                await self.callback_func(event.interaction)

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
