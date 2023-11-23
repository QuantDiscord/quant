from abc import ABC, abstractmethod


class Component(ABC):
    def __init__(self, custom_id: str | None) -> None:
        self.custom_id = custom_id

    @abstractmethod
    def as_json(self):
        pass
