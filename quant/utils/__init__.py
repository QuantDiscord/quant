"""
MIT License

Copyright (c) 2024 MagM1go

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
import logging

from quant.impl.core.exceptions.command_exceptions import NotEnoughPermissions
from quant.entities.permissions import Permissions
from quant.utils.cache.cacheable import CacheableType

__all__ = (
    "has_permissions",
    "logger",
    "CacheableType"
)


def has_permissions(member_permissions: Permissions, needed_permissions: Permissions) -> bool:
    if member_permissions == Permissions.NONE:
        return False

    if member_permissions == Permissions.ADMINISTRATOR or member_permissions & Permissions.ADMINISTRATOR:
        return True

    missing_permissions = needed_permissions & ~member_permissions
    if missing_permissions == Permissions.NONE:
        return True

    if missing_permissions is not None:
        raise NotEnoughPermissions(
            f"Missing permissions: {missing_permissions} ({missing_permissions.value})",
            missing=missing_permissions
        )

    return member_permissions.value & needed_permissions.value


logging.basicConfig(format="%(levelname)s | %(asctime)s %(module)s - %(message)s", level=logging.INFO)
logging.captureWarnings(True)


def _get_logger() -> logging.Logger:
    return logging.getLogger(__name__)


logger = _get_logger()
