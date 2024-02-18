from typing import List

import attrs

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
    components: List[ActionRow] = attrs.field()


@attrs.define(kw_only=True)
class ModalInteractionCallbackData:
    title: str = attrs.field()
    custom_id: str = attrs.field()
    components: List[ActionRow] = attrs.field()
