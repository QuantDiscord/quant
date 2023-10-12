import os

import quant
import lavasnek_rs
from dotenv import load_dotenv

from quant.data.gateway.snowflake import Snowflake

load_dotenv()


class LavalinkEventHandler:
    async def track_start(self, _, event: lavasnek_rs.TrackStart) -> None:
        print(f"Track started {event.track}")


YOUR_BOT_ID = 12344509234324
client = quant.Client(
    prefix="!",
    token=f"Bot {os.getenv('TOKEN')}",
    intents=quant.Intents.ALL
)
client.lavalink: lavasnek_rs.Lavalink | None = None  # type: ignore


async def on_voice_state_update(event: quant.VoiceStateUpdateEvent) -> None:
    client.lavalink.raw_handle_event_voice_state_update(
        event.state.guild_id,
        event.state.user_id,
        event.state.session_id,
        event.state.channel_id
    )


async def on_voice_server_update(event: quant.VoiceServerUpdateEvent) -> None:
    await client.lavalink.raw_handle_event_voice_server_update(
        event.state.guild_id,
        event.state.endpoint,
        event.state.token
    )


async def on_ready_callback(_: quant.ReadyEvent) -> None:
    builder = (
        lavasnek_rs.LavalinkBuilder(
            YOUR_BOT_ID, os.getenv("TOKEN")
        )
        .set_host("127.0.0.1")
        .set_port(8081)
        .set_password("your_lava_token")
        .set_start_gateway(False)
    )

    lavaclient = await builder.build(LavalinkEventHandler())
    client.lavalink = lavaclient


async def join_callback(ctx: quant.MessageCommandContext) -> None:
    voice_state = client.cache.get_voice_state(ctx.original_message.guild_id, ctx.original_message.author_as_user.user_id)

    channel_id = voice_state.channel_id

    await client.gateway.connect_voice(guild_id=ctx.original_message.guild_id, channel_id=channel_id)
    await ctx.send_message(content=f"Connected to <#{channel_id}>")
    connection = await client.lavalink.wait_for_full_connection_info_insert(ctx.original_message.guild_id)

    await client.lavalink.create_session(connection)


async def play_callback(ctx: quant.MessageCommandContext, *query: str) -> None:
    track = (await client.lavalink.auto_search_tracks(" ".join(query))).tracks[0]

    await client.lavalink.play(ctx.original_message.guild_id, track).requester(ctx.original_message.author_as_user.user_id).queue()
    await ctx.send_message(content=f"Now playing **{track.info.title}**")


def register_commands():
    commands = {
        quant.MessageCommand("join", "join voice"): join_callback,
        quant.MessageCommand("play", "Play song"): play_callback
    }

    for command, callback in commands.items():
        command.set_callback(callback)
        client.add_message_command(command)


register_commands()
client.add_listener(on_voice_state_update)
client.add_listener(on_voice_server_update)
client.add_listener(on_ready_callback)
client.run()
