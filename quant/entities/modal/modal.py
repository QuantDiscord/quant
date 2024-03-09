from __future__ import annotations

from typing import List, overload, TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from quant.entities.action_row import ActionRow

from quant.impl.core.context import ModalContext
from quant.entities.api.backend import CallbackBackend
from quant.entities.modal.text_input import TextInputStyle, TextInput


@attrs.define(kw_only=True)
class Modal(CallbackBackend[ModalContext]):
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
        from quant.entities.action_row import ActionRow

        if len(args) == 1:
            text_input = args[0]
        else:
            text_input = TextInput(style=TextInputStyle.SHORT.value, **kwargs)

        self.components.append(ActionRow([text_input]))

    @overload
    def add_paragraph_text_input(
        self,
        custom_id: str,
        label: str,
        min_length: int = 0,
        max_length: int = 4000,
        required: bool = True,
        value: str | None = None,
        placeholder: str | None = None
    ) -> None:
        """Append new paragraph text input"""

    def add_paragraph_text_input(self, *args, **kwargs) -> None:
        from quant.entities.action_row import ActionRow

        if len(args) == 1:
            text_input = args[0]
        else:
            text_input = TextInput(style=TextInputStyle.PARAGRAPH.value, **kwargs)

        self.components.append(ActionRow([text_input]))


@attrs.define(kw_only=True)
class ModalInteractionCallbackData:
    title: str = attrs.field()
    custom_id: str = attrs.field()
    components: List[ActionRow] = attrs.field()
