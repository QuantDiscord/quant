from functools import reduce

from dispy.impl.core.exceptions.library_exception import LibraryException


class Snowflake(int):
    DISCORD_EPOCH = 14_200_704_000_00
    INCREMENT = 0

    def __init__(self) -> None:
        self.timestamp = ((self >> 22) + self.DISCORD_EPOCH) / 1000
        self.object_id = self

    def generate_snowflake(
        self,
        timestamp: int,
        worker_id: int = 0,
        process_id: int = 0
    ) -> int:
        if timestamp <= self.DISCORD_EPOCH:
            raise LibraryException(f"Timestamp can't be earlier discord epoch ({self.DISCORD_EPOCH})")

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
