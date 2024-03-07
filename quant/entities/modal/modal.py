from typing import List, overload

import attrs

from quant.entities.modal.text_input import TextInputStyle, TextInput
from quant.entities.action_row import ActionRow


class ModalBackend:
    async def callback(self, context):
        pass

    callback_func = callback

    def set_callback(self, coro):
        self.callback_func = coro


@attrs.define(kw_only=True)
class Modal(ModalBackend):
    """Represents a discord modal window

    Parameters
    ==========
    title: :class:`str`
        Modal window title
    custom_id: :class:`str`
        Modal custom ID
    components: :class:`List[ActionRow]`
        Modal components
    """
    title: str = attrs.field(default="Modal")
    custom_id: str = attrs.field()
    components: List[ActionRow] = attrs.field(default=[])

    @overload
    def add_short_text_input(self, text_input: TextInput) -> None:
        """Append your short text input"""

    @overload
    def add_short_text_input(
        self,
        custom_id: str,
        label: str,
        min_length: int = 0,
        max_length: int = 4000,
        required: bool = True,
        value: str | None = None,
        placeholder: str | None = None
    ) -> None:
        """Append new short text input"""

    def add_short_text_input(self, *args, **kwargs) -> None:
        if len(args) == 1:
            text_input = args[0]
        else:
            text_input = TextInput(style=TextInputStyle.SHORT.value, **kwargs)

        self.components.append(ActionRow([text_input]))


@attrs.define(kw_only=True)
class ModalInteractionCallbackData:
    title: str = attrs.field()
    custom_id: str = attrs.field()
    components: List[ActionRow] = attrs.field()
