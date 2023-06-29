class Embed(dict):
    def __init__(
        self,
        title: str = None,
        description: str = None,
        fields: list[dict] = None
    ) -> None:
        super().__init__(
            type="rich",
            title=title,
            description=description,
            fields=fields
        )

        self.title = title
        self.description = description
        self.fields = fields
