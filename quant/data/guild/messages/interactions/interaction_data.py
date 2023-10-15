from typing import List, Any

import attrs

from quant.data.guild.messages.interactions.response.choice_response import ChoiceResponse
from quant.data.model import BaseModel
from quant.utils.attrs_extensions import int_converter
from quant.data.gateway.snowflake import Snowflake
from quant.data.guild.messages.interactions.application_command_option import ApplicationCommandOptionType


@attrs.define(kw_only=True)
class InteractionData(BaseModel):
    interaction_id: Snowflake = attrs.field(default=0, alias="id", converter=int_converter)
    component_type: int = attrs.field(default=0, converter=int_converter)
    interaction_type: int = attrs.field(default=None, converter=int_converter, alias="type")
    custom_id: str = attrs.field(default=None)
    name: str = attrs.field(default=None)
    option_type: ApplicationCommandOptionType = attrs.field(default=0, converter=int_converter)
    value: str | int | bool = attrs.field(default=None)
    options: List[ChoiceResponse] = attrs.field(default=None, converter=ChoiceResponse.as_dict_iter)
    focused: bool = attrs.field(default=False)
    components: List[Any] = attrs.field(default=None)
    resolved: bool = attrs.field(default=False)
