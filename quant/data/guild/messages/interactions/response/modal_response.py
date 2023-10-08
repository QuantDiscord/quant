from typing import List, Any

import attrs


@attrs.define(kw_only=True)
class ModalInteractionCallbackData:
    title: str = attrs.field()
    custom_id: str = attrs.field()
    components: List[Any] = attrs.field()
