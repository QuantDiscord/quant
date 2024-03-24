from __future__ import annotations

import os
from io import BytesIO
from abc import ABC, abstractmethod
from pathlib import Path
from urllib import parse


def file_to_bytes(file: File | None) -> bytes:
    if file is None:
        return bytes(0)

    buffer = BytesIO(file.path.read_bytes())
    return buffer.getvalue()


def get_image_ending(data: bytes) -> str | None:
    if data[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'
    elif data.startswith(b'\211PNG\r\n\032\n'):
        return 'png'
    elif data[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'webp'
    else:
        raise ValueError("Provided file type isn't image")


def get_image_mimetype(file: File):
    return "image/" + get_image_ending(file_to_bytes(file))


def is_image_file(file: File) -> bool:
    return get_image_ending(file_to_bytes(file)) is not None


class Attachable(ABC):
    @property
    @abstractmethod
    def url(self) -> str:
        """Attachment url"""

    @property
    @abstractmethod
    def filename(self) -> str:
        """Attachment filename"""


class File(Attachable):
    def __init__(self, path: Path | str, spoiler: bool = False) -> None:
        self.path = Path(path)
        self.spoiler = spoiler

        self._filename = self.path.name

    @property
    def filename(self) -> str:
        if self.spoiler:
            return "SPOILER_" + self._filename
        return self._filename

    @property
    def url(self) -> Path:
        return self.path.absolute()


class AttachableURL(Attachable):
    def __init__(self, url: str) -> None:
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    @property
    def filename(self) -> str:
        return os.path.basename(parse.urlparse(self.url).path)
