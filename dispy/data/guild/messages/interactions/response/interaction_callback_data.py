from typing import List, Any

import attrs

from dispy.data.guild.messages.embeds import Embed
from dispy.data.guild.messages.mentions.allowed_mentions import AllowedMentions
from dispy.data.model import BaseModel


@attrs.define(kw_only=True)
class InteractionCallbackData(BaseModel):
    tts: bool = attrs.field(default=False)
    content: str = attrs.field(default=None)
    embeds: List[Embed] = attrs.field(default=None)
    allowed_mentions: AllowedMentions = attrs.field(default=None)
    flags: int = attrs.field(default=0)
    components: Any = attrs.field(default=None)
    attachments: Any = attrs.field(default=None)
