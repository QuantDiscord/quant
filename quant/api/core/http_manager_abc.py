from typing import Final, Dict, Any
from abc import ABC, abstractmethod

from aiohttp import ClientResponse


class HttpManager(ABC):
    APPLICATION_JSON: Final[str] = "application/json"
    APPLICATION_X_WWW_FORM_URLENCODED: Final[str] = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA: Final[str] = "multipart/form-data"
    AUTHORIZATION: Final[str] = "Authorization"
    TEXT_HTML: Final[str] = "text/html"

    @staticmethod
    @abstractmethod
    async def send_request(method: str, url: str,
                           data: Dict[str, Any] = None,
                           headers: Dict[str, str] = None,
                           content_type: str = None) -> ClientResponse | None:
        raise NotImplementedError
