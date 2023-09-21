from typing import List
from abc import ABC, abstractmethod


class RESTAware(ABC):
    @abstractmethod
    async def delete_message(self, channel_id: int, message_id: int, reason: str = None):
        ...

    @abstractmethod
    async def create_message(
        self,
        content: str,
        nonce: str | int,
        tts: bool = None,
        embeds: List = None,
        allowed_mentions=None,
        message_reference=None,
        components: List = None,
        sticker_ids: List = None,
        files=None,
        payload_json: str = None,
        attachments: List = None,
        flags: int = None
    ):
        ...
