# DisPy - Discord API Framework

DisPy is a Python framework designed to simplify interaction with the Discord API and facilitate the development of Discord bots.

## Example Usage

Here's an example code showcasing how to use DisPy:

```python
from dispy.impl.core.client import Client
from dispy.data.intents import Intents
from dispy.impl.events.bot.ready_event import ReadyEvent

client = Client(
    token="YOUR_DISCORD_BOT_TOKEN",
    intents=Intents.ALL,
    mobile_status=True,
    prefix="!"
)


async def on_ready(event: ReadyEvent):
    print('Bot is ready!')


client.add_listener(ReadyEvent, on_ready)
client.run()
```
Replace `YOUR_DISCORD_BOT_TOKEN` with your actual Discord bot token.

# Getting Started
## Installation:
You can install DisPy using pip:

`pip install dispy`
Usage:

Create a new instance of Client by providing your Discord bot token and desired options.
Define callback functions for your commands and events.
Add commands and event listeners using the appropriate methods provided by the Client class.
Start the bot using client.run().

# Documentation:
Coming soon


# Contibuting:
Coming soon


# License:
DisPy is licensed under the MIT License. See the [LICENSE](https://github.com/MagM1go/dispy/blob/main/LICENSE) file for more details.
