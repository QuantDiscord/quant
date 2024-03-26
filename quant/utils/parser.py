"""
MIT License

Copyright (c) 2023 MagM1go

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING
from datetime import datetime

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
            return guild.get_channel(int(value))
        case _:
            return value


def parse_permissions(permission_value: int) -> Permissions:
    decoded_permissions = Permissions(0)
    for permission in Permissions:
        try:
            value = permission.value
        except TypeError:
            value = permission.value()

        if permission_value is None:
            return Permissions.NONE

        if permission_value & value == Permissions.ADMINISTRATOR.value:
            return Permissions.ADMINISTRATOR

        if permission_value & value == permission.value:
            decoded_permissions |= permission

    return decoded_permissions


def iso_to_datetime(time: str = None) -> datetime | None:
    if time is None:
        return

    return datetime.fromisoformat(time)


def timestamp_to_datetime(time: str | int = None) -> datetime | None:
    if time is None:
        return

    return datetime.fromtimestamp(time)
