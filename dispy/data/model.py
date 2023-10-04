from typing import Any


class BaseModel:
    client: Any | None = None

    @classmethod
    def set_client(cls, client: Any):
        cls.client = client

    @classmethod
    def as_dict(cls, data: dict):
        return cls(**data)  # type: ignore
