from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant.entities.permissions import Permissions

__all__ = (
    "has_permissions",
)


def has_permissions(member_permissions: Permissions, needed_permissions: Permissions) -> bool:
    return member_permissions.value & needed_permissions.value
