from dispy.impl.core import MessageCommandContext
from dispy.impl.core.client import Client, Intents
from dispy.impl.core.commands import MessageCommand
from dispy.impl.events.bot.ready_event import ReadyEvent
from dispy.impl.events.guild.message_events.reaction_add_event import ReactionAddEvent

client = Client(
    prefix="!",
    token="Bot NzkwODc4ODI1MzU2NzIyMTg3.GrXX0G.lfA4iBxkKWYZ1UJsliOstM0cRXYGVxTp4NlI_4",
    intents=Intents.ALL,
    mobile_status=True
)


async def emoji_cmd_callback(ctx: MessageCommandContext, emoji_id: int):
    emoji = await client.rest.fetch_emoji(ctx.original_message.guild_id, emoji_id)

    await ctx.send_message(content=emoji)


async def on_reaction_add(event: ReactionAddEvent):
    await client.rest.create_message(channel_id=1125053092522639372, content=str(event.reaction))


async def on_ready(event) -> None:
    print("Ready")

emoji_cmd = MessageCommand("emoji", "get emoji")
emoji_cmd.callback = emoji_cmd_callback

client.add_message_command(emoji_cmd)
client.add_listener(ReactionAddEvent, on_reaction_add)
client.add_listener(ReadyEvent, on_ready)
client.run()
