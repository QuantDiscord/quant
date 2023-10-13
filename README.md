# Quant - Discord API Framework

Quant is a Python framework designed to simplify interaction with the Discord API and facilitate the development of Discord bots.

## Example Usage

Here's an example code showcasing how to use quant:

```python
from quant import Client, Intents
from quant.events import ReadyEvent

client = Client(
    token="YOUR_DISCORD_BOT_TOKEN",  # you MUST set token prefix manually. Like `Bot YOUR_TOKEN`
    intents=Intents.ALL,
    mobile_status=True,
    prefix="!"
)


async def on_ready(event: ReadyEvent):
    print('Bot is ready!')


client.add_listener(on_ready)
client.run()
```
Replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord bot token.

# [Official support server](https://discord.gg/MnECK7DJ6n)

# Getting Started
## Installation:
You can install quant using pip:

`pip install quant`

# Usage:

Create a new instance of Client by providing your Discord bot token and desired options.
Define callback functions for your commands and events.
Add commands and event listeners using the appropriate methods provided by the Client class.
Start the bot using client.run().

# Documentation:
Coming soon


# Contibuting:
Coming soon


# License:
Quant is licensed under the MIT License. See the [LICENSE](https://github.com/MagM1go/quant/blob/main/LICENSE) file for more details.
