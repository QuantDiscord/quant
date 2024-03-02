import logging

from quant.entities.permissions import Permissions

__all__ = (
    "has_permissions",
    "logger"
)


def has_permissions(member_permissions: Permissions, needed_permissions: Permissions) -> bool:
    if member_permissions == Permissions.ADMINISTRATOR or member_permissions & Permissions.ADMINISTRATOR:
        return True

    return member_permissions.value & needed_permissions.value


logging.basicConfig(format="%(levelname)s | %(asctime)s %(module)s - %(message)s", level=logging.INFO)


def _get_logger() -> logging.Logger:
    return logging.getLogger(__name__)


logger = _get_logger()
