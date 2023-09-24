from dispy.impl.core.client import Client, Intents
from dispy.impl.events.bot.ready_event import ReadyEvent

client = Client(
    prefix="!",
    token="Bot NzkwODc4ODI1MzU2NzIyMTg3.Gbesek.lg7F5hj8-dRWmt80zPkt2E6p6B3UNTF3yW_SGo",
    intents=Intents.ALL
)


async def on_ready(event) -> None:
    print(client.cache.get_emojis())


client.add_listener(ReadyEvent, on_ready)
client.run()
