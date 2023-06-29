import asyncio

from impl.core.client import Client
from data.intents import Intents
from impl.events.bot.ready_event import ReadyEvent


client = Client(
    token="...",
    intents=Intents.ALL,
    with_mobile_status=True,
    prefix="!"
)


async def on_ready(event: ReadyEvent):
    print('started')

client.add_listener(ReadyEvent, on_ready)

loop = asyncio.get_event_loop()
loop.run_until_complete(client.run())
