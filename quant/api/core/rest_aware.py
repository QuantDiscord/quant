from typing import List, Any, Dict
from abc import ABC, abstractmethod

from quant.entities.interactions.slash_option import SlashOption
from quant.entities.guild import Guild
from quant.entities.emoji import Emoji
from quant.entities.interactions.interaction import InteractionCallbackType, InteractionCallbackData
from quant.entities.allowed_mentions import AllowedMentions
from quant.entities.message import Message
from quant.entities.embeds import Embed
from quant.entities.webhook import Webhook


class RESTAware(ABC):
    @abstractmethod
    async def execute_webhook(
        self,
        webhook_url: str,
        content: str = None,
        username: str = None,
        avatar_url: str = None,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        components: List[Any] = None,
        files: List[Any] = None,
        payload_json: str = None,
        attachments: List[Any] = None,
        flags: int = None,
        thread_name: str = None
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_webhook(self, channel_id: int, name: str, avatar: str = None, reason: str = None) -> Webhook:
        raise NotImplementedError

    @abstractmethod
    async def fetch_emoji(self, guild_id: int, emoji: str) -> Emoji:
        raise NotImplementedError

    @abstractmethod
    async def create_reaction(
        self,
        emoji: str,
        guild_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        reason: str = None
    ) -> Emoji | str:
        raise NotImplementedError

    @abstractmethod
    async def delete_message(self, channel_id: int, message_id: int, reason: str = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_message(
        self,
        channel_id: int,
        content: str = None,
        nonce: str | int = None,
        tts: bool = False,
        embed: Embed = None,
        embeds: List[Embed] = None,
        allowed_mentions: AllowedMentions = None,
        message_reference=None,
        components: List[Dict[str, Any]] = None,
        sticker_ids: List = None,
        files=None,
        payload_json: str = None,
        attachments: List = None,
        flags: int = None
    ):
        raise NotImplementedError

    @abstractmethod
    async def fetch_guild(self, guild_id: int, with_counts: bool = False) -> Guild:
        raise NotImplementedError

    @abstractmethod
    async def delete_guild(self, guild_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_guild(
        self,
        name: str,
        region: str = None,
        icon: Any = None,
        verification_level: int | None = None,
        default_message_notifications: int | None = None,
        explicit_content_filter: int | None = None,
        roles: List[Any] = None,
        channels: List[Any] = None,
        afk_channel_id: int | None = None,
        afk_timeout: int | None = None,
        system_channel_id: int | None = None,
        system_channel_flags: int = 0
    ) -> Guild:
        raise NotImplementedError

    @abstractmethod
    async def create_interaction_response(
        self, interaction_type: InteractionCallbackType,
        interaction_data: InteractionCallbackData, interaction_id: int,
        interaction_token: str
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def fetch_message(self, channel_id: int, message_id: int) -> Message:
        raise NotImplementedError

    @abstractmethod
    async def create_application_command(
        self,
        application_id: int,
        name: str,
        description: str,
        default_permissions: bool = False,
        dm_permissions: bool = False,
        default_member_permissions: str = None,
        guild_id: int | None = None,
        options: List[SlashOption] = None,
        nsfw: bool = False
    ) -> None:
        raise NotImplementedError
