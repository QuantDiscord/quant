import enum
from typing import List

import attrs


@attrs.define
class AllowedMentions:
    parse: List[str] = attrs.field()
    roles: List[int] = attrs.field(default=list())
    users: List[int] = attrs.field(default=list())
    replied_user: bool = attrs.field(default=False)


class AllowedMentionsTypes(enum.Enum):
    ROLE_MENTIONS = "roles"
    USER_MENTIONS = "users"
    EVERYONE_MENTIONS = "everyone"

    ROLE_AND_USER = [ROLE_MENTIONS, USER_MENTIONS]
    ROLE_AND_EVERYONE = [ROLE_MENTIONS, EVERYONE_MENTIONS]

    USER_AND_EVERYONE = [USER_MENTIONS, EVERYONE_MENTIONS]

    ALL = [ROLE_MENTIONS, USER_MENTIONS, EVERYONE_MENTIONS]
