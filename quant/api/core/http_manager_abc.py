from typing import Final, Dict, Any
from abc import ABC, abstractmethod

from aiohttp import ClientResponse

from quant.utils.json_builder import MutableJsonBuilder


class HttpManager(ABC):
    APPLICATION_JSON: Final[str] = "application/json"
    APPLICATION_X_WWW_FORM_URLENCODED: Final[str] = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA: Final[str] = "multipart/form-data"
    AUTHORIZATION: Final[str] = "Authorization"
    TEXT_HTML: Final[str] = "text/html"

    @abstractmethod
    async def send_request(
        self,
        method: str, url: str,
        data: Dict[str, Any] | MutableJsonBuilder[str, Any] = None,
        headers: Dict[str, str] | MutableJsonBuilder[str, Any] = None,
        content_type: str = None
    ) -> ClientResponse | None:
        raise NotImplementedError
