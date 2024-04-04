import quant


client = quant.Client(token="...")


async def say_command_callback(context: quant.InteractionContext) -> None:
    message = await context.get_option("message")
    allowed_mentions = quant.AllowedMentions(parse=[quant.AllowedMentionsTypes.ALL.value])
    await context.interaction.respond(content=" ".join(message), allowed_mentions=allowed_mentions)


say_command = quant.SlashCommand(name="say", description="Say something")
say_command.option(name="message", description="Echo message", required=True)
say_command.set_callback(say_command_callback)

client.add_slash_command(say_command)
client.run()


# Or you can make like this:
class SayCommand(quant.SlashCommand):
    def __init__(self) -> None:
        super().__init__(name="say", description="say something", options=[
            quant.ApplicationCommandOption(name="message", description="Echo message")
        ])

    # Here lint warning, I fix that later
    async def callback(self, context: quant.InteractionContext) -> None:
        message = await context.get_option("message")
        await context.interaction.respond(content=message)


client.add_slash_command(SayCommand())
client.run()
