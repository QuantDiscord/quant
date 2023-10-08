from typing import List, Any

import attrs

from quant.data.model import BaseModel
from quant.utils.attrs_extensions import snowflake_to_int
from quant.data.gateway.snowflake import Snowflake
from quant.data.guild.messages.interactions.application_command_option import ApplicationCommandOptionType


@attrs.define(kw_only=True)
class InteractionData(BaseModel):
    interaction_id: Snowflake = attrs.field(default=0, alias="id", converter=snowflake_to_int)
    component_type: int = attrs.field(default=0, converter=snowflake_to_int)
    interaction_type: int = attrs.field(default=None, converter=snowflake_to_int, alias="type")
    custom_id: str = attrs.field()
    name: str = attrs.field(default=None)
    option_type: ApplicationCommandOptionType = attrs.field(default=0, converter=int)
    value: str | int | bool = attrs.field(default=None)
    options: List[Any] = attrs.field(default=None)
    focused: bool = attrs.field(default=False)
    components: List[Any] = attrs.field(default=None)
