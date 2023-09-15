import asyncio

from impl.core.client import Client
from data.intents import Intents
from impl.events.bot.ready_event import ReadyEvent
from impl.core.commands import Command


client = Client(
    token="...",
    intents=Intents.ALL,
    with_mobile_status=True,
    prefix="!"
)


async def test_command_callback(bot: Client) -> None:
    await bot.rest.create_message(channel_id=..., content="aboba")

async def on_ready(event: ReadyEvent):
    print('started')


client.commands["test"] = test_command_callback
client.add_listener(ReadyEvent, on_ready)

loop = asyncio.get_event_loop()
loop.run_until_complete(client.run())
