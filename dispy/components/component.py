from abc import ABC, abstractmethod

from dispy.data.model import BaseModel


class Component(ABC, BaseModel):
    def __init__(self, custom_id: str | None) -> None:
        self.custom_id = custom_id

    @abstractmethod
    def as_json(self):
        pass
