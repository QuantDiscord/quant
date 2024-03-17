from typing import List, Any
from datetime import datetime

import attrs
from attrs import define, field


@define
class EmbedField:
    name: str
    value: Any
    inline: bool = False


@define
class EmbedFooter:
    text: Any
    icon_url: str | None = None
    proxy_icon_url: str | None = None


@define
class EmbedAuthor:
    name: str
    url: str | None = None
    icon_url: str | None = None
    proxy_icon_url: str | None = None


@define
class EmbedImage:
    url: str
    proxy_url: str | None = None
    height: int | None = None
    width: int | None = None
    placeholder: str = attrs.field(default=None, repr=False)
    placeholder_version: int = attrs.field(default=None, repr=False)


EmbedThumbnail = EmbedImage


@define
class Embed:
    title: str = field()
    description: str = field()
    url: str = field()
    timestamp: datetime = field()
    color: str | int = field()
    footer: EmbedFooter = field()
    image: EmbedImage = field()
    thumbnail: EmbedThumbnail = field()
    author: EmbedAuthor = field()
    fields: List[EmbedField] = field()
    _type: str = field(alias="type", default="rich")


def embed(
    title: str | None = None,
    description: str | None = None,
    url: str | None = None,
    timestamp: datetime | None = None,
    color: str | int | None = None,
    footer: EmbedFooter | None = None,
    image: EmbedImage | str | None = None,
    thumbnail: EmbedThumbnail | str | None = None,
    author: EmbedAuthor | None = None,
    fields: List[EmbedField] | None = None,
) -> Embed:
    if isinstance(image, str):
        image = EmbedImage(url=image, proxy_url=None, width=1024, height=1024)

    return Embed(
        title=title,
        description=description,
        url=url,
        timestamp=timestamp,
        color=color,
        footer=footer,
        image=image,
        thumbnail=thumbnail,
        author=author,
        fields=fields
    )
