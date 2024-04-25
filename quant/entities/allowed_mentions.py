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
import enum
from typing import List

import attrs


@attrs.define(hash=True)
class AllowedMentions:
    parse: List[str] = attrs.field()
    roles: List[int] = attrs.field(default=list())
    users: List[int] = attrs.field(default=list())
    replied_user: bool = attrs.field(default=False)


class AllowedMentionsTypes(enum.Enum):
    ROLE_MENTIONS = "roles"
    USER_MENTIONS = "users"
    EVERYONE_MENTIONS = "everyone"

    ROLE_AND_USER = [ROLE_MENTIONS, USER_MENTIONS]
    ROLE_AND_EVERYONE = [ROLE_MENTIONS, EVERYONE_MENTIONS]

    USER_AND_EVERYONE = [USER_MENTIONS, EVERYONE_MENTIONS]

    ALL = [ROLE_MENTIONS, USER_MENTIONS, EVERYONE_MENTIONS]


def suppress_mentions(
    roles: bool = False,
    users: bool = False,
    replied_user: bool = False,
    everyone: bool = False,
    suppress_all: bool = False
) -> AllowedMentions:
    if all((roles, users, replied_user, everyone)) is False:
        return AllowedMentions(parse=[])

    if suppress_all:
        return AllowedMentions(parse=[])

    parse = []
    if roles:
        parse.append(AllowedMentionsTypes.ROLE_MENTIONS.value)
    if users:
        parse.append(AllowedMentionsTypes.USER_MENTIONS.value)
    if everyone:
        parse.append(AllowedMentionsTypes.EVERYONE_MENTIONS.value)

    return AllowedMentions(parse=parse, replied_user=replied_user)
