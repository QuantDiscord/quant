from typing import List

import attrs


@attrs.define
class AllowedMentions:
    parse: List[str] = attrs.field()
    roles: List[int] = attrs.field(default=list())
    users: List[int] = attrs.field(default=list())
    replied_user: bool = attrs.field(default=False)
