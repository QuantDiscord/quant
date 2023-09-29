import dispy


client = dispy.Client(token="...", intents=dispy.Intents.ALL)


async def on_ready(event: dispy.ReadyEvent):
    print("Bot is ready.")


client.add_listener(on_ready)


# OR
async def on_ready(event):
    print("Bot is ready.")

client.add_listener(dispy.ReadyEvent, on_ready)
client.run()
