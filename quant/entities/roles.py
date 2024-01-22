from typing import List, Any

import attrs

from .snowflake import Snowflake


@attrs.define(kw_only=True)
class GuildRole:
    id: Snowflake = attrs.field()
    name: str = attrs.field()
    color: int = attrs.field()
    hoist: bool = attrs.field()
    icon: str | None = attrs.field()
    unicode_emoji: str | None = attrs.field()
    position: int = attrs.field()
    permissions: str = attrs.field()
    managed: bool = attrs.field()
    mentionable: bool = attrs.field()
    tags: List[Any] = attrs.field()
    flags: int = attrs.field()
