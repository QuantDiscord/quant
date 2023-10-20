from typing import Final,Dict,Any
from abc import ABC,abstractmethod
from aiohttp import ClientResponse
class HttpManager(ABC):
        APPLICATION_JSON='application/json';APPLICATION_X_WWW_FORM_URLENCODED='application/x-www-form-urlencoded';MULTIPART_FORM_DATA='multipart/form-data';AUTHORIZATION='Authorization';TEXT_HTML='text/html'
        @staticmethod
        @abstractmethod
        async def send_request(method,url,data=None,headers=None,content_type=None):raise NotImplementedError