from __future__ import annotations
from functools import reduce


class SnowflakeException(Exception):
    ...


class Snowflake(int):
    DISCORD_EPOCH = 14_200_704_000_00
    INCREMENT = 0

    def __new__(cls, object_id: int) -> Snowflake:
        return super().__new__(cls, object_id)

    def __init__(self, object_id: int) -> None:
        self.object_id = object_id
        self.timestamp = ((object_id >> 22) + self.DISCORD_EPOCH) / 1000

    def generate_snowflake(
        self,
        timestamp: int,
        worker_id: int = 0,
        process_id: int = 0
    ) -> int:
        if timestamp <= self.DISCORD_EPOCH:
            raise SnowflakeException(f"Timestamp can't be earlier than discord epoch ({self.DISCORD_EPOCH})")

        self.INCREMENT += 1

        snowflake_segments = [
            (timestamp - self.DISCORD_EPOCH) << 22,
            worker_id << 17,
            process_id << 12,
            self.INCREMENT
        ]

        if self.INCREMENT >= 4096:
            self.INCREMENT = 0

        return reduce(lambda x, y: x + y, snowflake_segments)
