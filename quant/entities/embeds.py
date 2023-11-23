from typing import List, Any
from datetime import datetime

from attrs import define, asdict


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


EmbedThumbnail = EmbedImage


class Embed(dict):
    def __init__(
        self,
        title: str = None,
        description: str = None,
        url: str = None,
        timestamp: datetime = None,
        color: str = None,
        footer: EmbedFooter = None,
        image: EmbedImage = None,
        thumbnail: EmbedThumbnail = None,
        author: EmbedAuthor = None,
        fields: List[EmbedField] = None
    ) -> None:
        super().__init__(
            type="rich",
            title=title,
            description=description,
            url=url,
            timestamp=timestamp,
            color=color,
            footer=asdict(footer) if footer is not None else None,
            image=asdict(image) if image is not None else None,
            thumbnail=asdict(thumbnail) if thumbnail is not None else None,
            author=asdict(author) if author is not None else None,
            fields=[asdict(i) for i in fields] if fields is not None else None
        )

        self.title = title
        self.description = description
        self.url = url
        self.timestamp = timestamp
        self.color = color
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail
        self.author = author
        self.fields = fields
