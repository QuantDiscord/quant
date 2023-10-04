from dispy.data.model import BaseModel


class Component(BaseModel):
    def __init__(self, custom_id: str | None) -> None:
        self.custom_id = custom_id
