class Command:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    async def callback(self, bot) -> None:
        pass
