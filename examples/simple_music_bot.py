import os
from typing import TypeVar

import quant
import lavasnek_rs
from dotenv import load_dotenv

load_dotenv()

LavalinkT = TypeVar("LavalinkT", bound=lavasnek_rs.Lavalink | None)


class MusicBot(quant.Client):
    def __init__(self) -> None:
        super().__init__(token=f"Bot {os.getenv('TOKEN')}")
        self._lavalink: LavalinkT = None

    @property
    def lavalink(self) -> LavalinkT:
        return self._lavalink

    @lavalink.setter
    def lavalink(self, value: lavasnek_rs.Lavalink) -> None:
        self._lavalink = value


client = MusicBot()


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
            client.me.id, os.getenv("TOKEN")
        )
        .set_host("127.0.0.1")
        .set_port(8081)
        .set_password("your_lava_token")
        .set_start_gateway(False)
    )

    event_handler = type("EventHandler", (), {})
    lava_client = await builder.build(event_handler)
    client.lavalink = lava_client


async def join_callback(ctx: quant.InteractionContext) -> None:
    guild_id = ctx.interaction.guild_id
    voice_state = client.cache.get_voice_state(guild_id, ctx.author.id)
    channel_id = voice_state.channel_id

    await client.gateway.connect_voice(guild_id=guild_id, channel_id=channel_id)
    await ctx.interaction.respond(content=f"Connected to <#{channel_id}>")
    connection = await client.lavalink.wait_for_full_connection_info_insert(guild_id)

    await client.lavalink.create_session(connection)


async def play_callback(ctx: quant.InteractionContext) -> None:
    query = await ctx.get_option("query")
    auto_search = await client.lavalink.auto_search_tracks(" ".join(query))
    track = auto_search.tracks[0]

    await client.lavalink.play(ctx.interaction.guild_id, track).requester(ctx.author.id).queue()
    await ctx.interaction.respond(content=f"Now playing **{track.info.title}**")


def register_commands():
    commands = {
        quant.SlashCommand(name="join", description="join voice"): join_callback,
        quant.SlashCommand(name="play", description="Play song", options=[
            quant.ApplicationCommandOption(name="query", description="Music name or smth", required=True)
        ]): play_callback
    }

    for command, callback in commands.items():
        command.set_callback(callback)
        client.add_slash_command(command)


def register_listener():
    callbacks = [on_ready_callback, on_voice_state_update, on_voice_server_update]

    for callback in callbacks:
        client.add_listener(callback)


register_commands()
register_listener()

client.run()
