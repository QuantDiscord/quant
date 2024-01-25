from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from quant.impl.core.client import Client
    from quant.entities.interactions.interaction import Interaction

from quant.entities.interactions.slash_option import SlashOptionType


async def parse_option_type(
    client: Client,
    interaction: Interaction,
    option_type: SlashOptionType,
    value: Any
) -> Any | None:
    guild = interaction.guild

    match option_type:
        case SlashOptionType.USER:
            return await client.rest.fetch_user(value)
        case SlashOptionType.ROLE:
            return guild.get_role(value)
        case SlashOptionType.CHANNEL:
            return guild.get_channel(value)
        case _:
            return value
