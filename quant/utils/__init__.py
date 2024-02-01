from quant.entities.permissions import Permissions

__all__ = (
    "has_permissions",
)


def has_permissions(member_permissions: Permissions, needed_permissions: Permissions) -> bool:
    if member_permissions == Permissions.ADMINISTRATOR or member_permissions & Permissions.ADMINISTRATOR:
        return True

    return member_permissions.value & needed_permissions.value
