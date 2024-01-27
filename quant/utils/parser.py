from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from quant.impl.core.client import Client
    from quant.entities.interactions.interaction import Interaction

from quant.entities.permissions import Permissions
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
            return await client.rest.fetch_user(int(value))
        case SlashOptionType.ROLE:
            return guild.get_role(int(value))
        case SlashOptionType.CHANNEL:
            return guild.get_channel(value)
        case _:
            return value


def decode_permissions(permission_value: int) -> Permissions:
    decoded_permissions = Permissions(0)
    for permission in Permissions:
        if permission_value & permission.value == permission.value:  # type: ignore
            decoded_permissions |= permission

    return decoded_permissions
