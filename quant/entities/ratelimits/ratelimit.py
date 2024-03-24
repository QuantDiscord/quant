import attrs


@attrs.define(kw_only=True)
class RateLimit:
    max_retries: int = attrs.field()
    remaining_retries: int = attrs.field()
    retry_after: float = attrs.field()
    message: str = attrs.field()
    is_global: bool = attrs.field()
    bucket: str = attrs.field()
    code: int | None = attrs.field()
    scope: str | None = attrs.field()
