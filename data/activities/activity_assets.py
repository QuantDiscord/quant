import attrs


@attrs.define
class ActivityAssets:
    large_image: str = attrs.field(default=None)
    large_text: str = attrs.field(default=None)
    small_image: str = attrs.field(default=None)
    small_text: str = attrs.field(default=None)
