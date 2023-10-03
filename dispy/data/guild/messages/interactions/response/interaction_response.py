import attrs

from dispy.data.guild.messages.interactions.response.interaction_callback_type import InteractionCallbackType
from dispy.data.guild.messages.interactions.response.interaction_callback_data import InteractionCallbackData
from dispy.data.model import BaseModel


@attrs.define(kw_only=True)
class InteractionResponse(BaseModel):
    interaction_response_type: InteractionCallbackType = attrs.field(default=InteractionCallbackType.PONG, alias="type")
    interaction_response_data: InteractionCallbackData = attrs.field(default=None)
