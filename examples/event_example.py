import quant


client = quant.Client(token="...", intents=quant.Intents.ALL)


async def on_ready(event: quant.ReadyEvent):
    print("Bot is ready.")


client.add_listener(on_ready)


# OR
async def on_ready(event):
    print("Bot is ready.")

client.add_listener(quant.ReadyEvent, on_ready)
client.run()
