from typing import List, Any

import attrs

from dispy.data.guild.messages.interactions.application_command_option import ApplicationCommandOptionType


@attrs.define(kw_only=True)
class InteractionData:
    name: str = attrs.field(default=None)
    option_type: ApplicationCommandOptionType = attrs.field(default=0, converter=int)
    value: str | int | bool = attrs.field(default=None)
    options: List[Any] = attrs.field(default=None)
    focused: bool = attrs.field(default=False)
