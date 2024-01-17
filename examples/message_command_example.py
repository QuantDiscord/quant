import quant


client = quant.Client(prefix="!", intents=Intents.ALL_UNPRIVILEGED, token="...")


async def say_command_callback(context: quant.InteractionContext, *message: str) -> None:
    allowed_mentions = quant.AllowedMentions(parse=[quant.AllowedMentionsTypes.ALL.value])
    await context.send_message(content=" ".join(message), allowed_mentions=allowed_mentions)


say_command = quant.SlashCommand(name="say", description="Say something")
say_command.set_callback(say_command_callback)

client.add_message_command(say_command)
client.run()


# Or you can make like this:
class SayCommand(quant.SlashCommand):
    def __init__(self) -> None:
        super().__init__("say", "say something")

    async def callback(self, context: quant.InteractionContext, *message: str) -> None:
        await context.send_message(content=" ".join(message))


client.add_slash_command(SayCommand())
client.run()
