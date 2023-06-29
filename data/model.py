from typing import Any

from dispy.data.gateway import Snowflake


def snowflake_converter(received_data=None):
    if received_data is None:
        return Snowflake(0)

    return Snowflake(int(received_data))


class BaseModel:
    client: Any | None = None

    @classmethod
    def set_client(cls, client: Any):
        cls.client = client

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)  # type: ignore
