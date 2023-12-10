<p align="center">
    <a href="https://discord.gg/MnECK7DJ6n">
        <img width="2100px" src="https://media.discordapp.net/attachments/1130594736944726106/1183271884175986688/Frame_1222.png?ex=6587bad1&is=657545d1&hm=9e223a5cb45271eae4cd2a56d994ed81030c4902d12f105a984554e807038086&=&format=webp&quality=lossless&width=1012&height=339" alt="banner">
    </a>
</p>

## Example Usage

Here's an example code showcasing how to use quant:

```python
from quant import Client, Intents
from quant.events import ReadyEvent

client = Client(
    token="Bot YOUR_DISCORD_BOT_TOKEN",
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

# Slash Commands

```python
from quant import (
    Client,
    SlashCommand,
    SlashOption,
    InteractionContext
)

client = Client(token="Bot YOUR_DISCORD_BOT_TOKEN")


# Echo bot
async def slash_command_callback(context: InteractionContext) -> None:
    value = context.interaction.interaction_data.options[0].value
    await context.interaction.respond(content=value)


command = SlashCommand(
    name="say",
    description="Say something",
    options=[
        SlashOption(name="text", description="your text", required=True)
    ]
)
command.set_callback(slash_command_callback)

client.run()
```

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
Coming soon.


# Contibuting:
Coming soon.


# License:
Quant is licensed under the MIT License. See the [LICENSE](https://github.com/MagM1go/quant/blob/main/LICENSE) file for more details.
