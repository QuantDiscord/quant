from quant.impl.core.context import MessageCommandContext
from quant.impl.core.commands import MessageCommand
from quant.entities.guild.messages.mentions.allowed_mentions import AllowedMentions
from quant.entities.guild.messages.mentions.allowed_mentions_types import AllowedMentionsTypes
from quant.impl.core.client import Client
from quant.entities.intents import Intents


client = Client(prefix="!", intents=Intents.ALL_UNPRIVILEGED, token="...")


async def say_command_callback(context: MessageCommandContext, *message: str) -> None:
    allowed_mentions = AllowedMentions(parse=[AllowedMentionsTypes.ALL.value])
    await context.send_message(content=" ".join(message), allowed_mentions=allowed_mentions)


say_command = MessageCommand(name="say", description="Say something")
say_command.callback = say_command_callback

client.add_message_command(say_command)
client.run()


# Or you can make like this:
class SayCommand(MessageCommand):
    def __init__(self) -> None:
        super().__init__("say", "say something")

    async def callback(self, context: MessageCommandContext, *message: str) -> None:
        await context.send_message(content=" ".join(message))


client.add_message_command(SayCommand())
client.run()
