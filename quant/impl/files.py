from __future__ import annotations

from io import BytesIO
from abc import ABC, abstractmethod
from pathlib import Path


def file_to_bytes(file: File | None) -> bytes:
    if file is None:
        return bytes(0)

    buffer = BytesIO(file.path.read_bytes())
    return buffer.getvalue()


def _is_image_ending(file: File) -> str | None:
    data = file_to_bytes(file)
    mimetype = "image/"

    if data[6:10] in (b'JFIF', b'Exif'):
        mimetype += 'jpeg'
    elif data.startswith(b'\211PNG\r\n\032\n'):
        mimetype += 'png'
    elif data[:6] in (b'GIF87a', b'GIF89a'):
        mimetype += 'gif'
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        mimetype += 'webp'
    else:
        raise ValueError("Provided file type isn't image")

    return mimetype


def is_image_file(file: File) -> bool:
    return _is_image_ending(file) is not None


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
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

        self._filename = self.path.name

    @property
    def filename(self) -> str:
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
        return ""
