import attrs


@attrs.define(kw_only=True)
class SessionStartLimitObject:
    total: int = attrs.field()
    remaining: int = attrs.field()
    reset_after: int = attrs.field()
    max_concurrency: int = attrs.field()


@attrs.define(kw_only=True)
class GatewayInfo:
    url: str = attrs.field()
    shards: int = attrs.field()
    session_start_limit: SessionStartLimitObject = attrs.field()
