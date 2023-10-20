_B=False
_A=None
from typing import List,Any,Dict
from abc import ABC,abstractmethod
from quant.data.guild.messages.interactions.slashes.slash_option import SlashOption
from quant.data.guild.guild_object import Guild
from quant.data.guild.messages.emoji import Emoji
from quant.data.guild.messages.interactions.response.interaction_callback_data import InteractionCallbackData
from quant.data.guild.messages.interactions.response.interaction_callback_type import InteractionCallbackType
from quant.data.guild.messages.mentions import AllowedMentions
from quant.data.guild.messages.message import Message
from quant.data.guild.messages.embeds import Embed
from quant.data.guild.webhooks.webhook import Webhook
class RESTAware(ABC):
        @abstractmethod
        async def execute_webhook(self,webhook_url,content=_A,username=_A,avatar_url=_A,tts=_B,embed=_A,embeds=_A,allowed_mentions=_A,components=_A,files=_A,payload_json=_A,attachments=_A,flags=_A,thread_name=_A):raise NotImplementedError
        @abstractmethod
        async def create_webhook(self,channel_id,name,avatar=_A,reason=_A):raise NotImplementedError
        @abstractmethod
        async def fetch_emoji(self,guild_id,emoji):raise NotImplementedError
        @abstractmethod
        async def create_reaction(self,emoji,guild_id=_A,channel_id=_A,message_id=_A,reason=_A):raise NotImplementedError
        @abstractmethod
        async def delete_message(self,channel_id,message_id,reason=_A):raise NotImplementedError
        @abstractmethod
        async def create_message(self,channel_id,content=_A,nonce=_A,tts=_B,embed=_A,embeds=_A,allowed_mentions=_A,message_reference=_A,components=_A,sticker_ids=_A,files=_A,payload_json=_A,attachments=_A,flags=_A):raise NotImplementedError
        @abstractmethod
        async def fetch_guild(self,guild_id,with_counts=_B):raise NotImplementedError
        @abstractmethod
        async def delete_guild(self,guild_id):raise NotImplementedError
        @abstractmethod
        async def create_guild(self,name,region=_A,icon=_A,verification_level=_A,default_message_notifications=_A,explicit_content_filter=_A,roles=_A,channels=_A,afk_channel_id=_A,afk_timeout=_A,system_channel_id=_A,system_channel_flags=0):raise NotImplementedError
        @abstractmethod
        async def create_interaction_response(self,interaction_type,interaction_data,interaction_id,interaction_token):raise NotImplementedError
        @abstractmethod
        async def fetch_message(self,channel_id,message_id):raise NotImplementedError
        @abstractmethod
        async def create_application_command(self,application_id,name,description,default_permissions=_B,dm_permissions=_B,default_member_permissions=_A,guild_id=_A,options=_A,nsfw=_B):raise NotImplementedError