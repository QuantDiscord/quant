from functools import reduce

from dispy.impl.core.exceptions.library_exception import LibraryException


class Snowflake:
    DISCORD_EPOCH = 1420070400000
    INCREMENT = 0

    def __init__(self, object_id: int | None = None) -> None:
        if object_id is not None:
            object_id = int(object_id)
            self.timestamp = ((object_id >> 22) + self.DISCORD_EPOCH) / 1000
            self.object_id = object_id

    @classmethod
    def to_snowflake(cls, snowflake_id):
        return cls(object_id=snowflake_id)

    @classmethod
    def object_id_from_snowflake(cls, obj_id: int) -> int:
        instance = cls(obj_id)

        if hasattr(instance, "object_id"):
            return instance.object_id

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
