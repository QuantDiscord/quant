from os import getenv
from typing import TypeVar, List

from dotenv import load_dotenv
from lavasnek_rs import Lavalink

from loader import register_components
from quant import Client, Intents, SlashCommand

load_dotenv()

LavalinkT = TypeVar("LavalinkT", bound=Lavalink | None)


class Bot(Client):
    def __init__(self) -> None:
        super().__init__(token=f"Bot {getenv('TOKEN')}", intents=Intents.ALL_UNPRIVILEGED, sync_commands=False)
        self._lavalink: LavalinkT = None
        self._commands: List[SlashCommand] | None = None

    @property
    def lavalink(self) -> LavalinkT:
        return self._lavalink

    @lavalink.setter
    def lavalink(self, value: Lavalink) -> None:
        self._lavalink = value

    @property
    def commands(self) -> List[SlashCommand]:
        if self._commands is None:
            self._commands = []
            return self._commands

        return self._commands


if __name__ == "__main__":
    client = Bot()
    register_components(bot=client)

    client.run()
