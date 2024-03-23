from abc import ABC, abstractmethod
from typing import Final, Dict, Any

from aiohttp import ClientResponse


class AcceptContentType:
    APPLICATION_JSON: Final[str] = "application/json"
    APPLICATION_X_WWW_FORM_URLENCODED: Final[str] = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA: Final[str] = "multipart/form-data"
    AUTHORIZATION: Final[str] = "Authorization"
    TEXT_HTML: Final[str] = "text/html"

    class MimeTypes:
        IMAGE_PNG: Final[str] = "image/png"
        IMAGE_JPG: Final[str] = "image/jpg"
        IMAGE_GIF: Final[str] = "image/gif"
        IMAGE_WEBP: Final[str] = "image/webp"


class HttpManager(ABC):
    @abstractmethod
    async def request(
        self,
        method: str, url: str,
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> ClientResponse | None:
        raise NotImplementedError
