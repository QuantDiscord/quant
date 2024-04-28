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
from functools import reduce
from typing import TypeVar


class SnowflakeException(Exception):
    ...


class Snowflake(int):
    DISCORD_EPOCH = 14_200_704_000_00

    def __new__(cls, object_id: int | str | None = None):
        if object_id is None:
            return Snowflake(0)

        return super().__new__(cls, int(object_id))

    def __init__(self, object_id: int | str | None = None) -> None:
        if object_id is None:
            object_id = 0

        self.object_id = int(object_id)
        self.timestamp = ((self.object_id >> 22) + self.DISCORD_EPOCH) / 1000
        self.increment = 0

    def generate_snowflake(
        self,
        timestamp: int,
        worker_id: int = 0,
        process_id: int = 0
    ) -> int:
        if timestamp <= self.DISCORD_EPOCH:
            raise SnowflakeException(f"Timestamp can't be earlier than discord epoch ({self.DISCORD_EPOCH})")

        self.increment += 1

        snowflake_segments = [
            (timestamp - self.DISCORD_EPOCH) << 22,
            worker_id << 17,
            process_id << 12,
            self.increment
        ]

        if self.increment >= 4096:
            self.increment = 0

        return reduce(lambda x, y: x + y, snowflake_segments)


SnowflakeOrInt = TypeVar("SnowflakeOrInt", bound=Snowflake | int)
