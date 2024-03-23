from datetime import datetime

import attrs


@attrs.define(kw_only=True)
class RateLimit:
    max_retries: int = attrs.field()
    remaining_retries: int = attrs.field()
    ratelimit_reset: datetime = attrs.field()
    retry_after: float = attrs.field()
    message: str = attrs.field()
    is_global: bool = attrs.field()
    code: int | None = attrs.field()
