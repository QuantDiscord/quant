from __future__ import annotations as _

from os import getenv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot

from quant import VoiceStateUpdateEvent, VoiceServerUpdateEvent, InteractionContext, ReadyEvent
from lavasnek_rs import LavalinkBuilder


class MusicModule:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def on_voice_state_update(self, event: VoiceStateUpdateEvent) -> None:
        self.bot.lavalink.raw_handle_event_voice_state_update(
            event.state.guild_id,
            event.state.user_id,
            event.state.session_id,
            event.state.channel_id
        )

    async def on_voice_server_update(self, event: VoiceServerUpdateEvent) -> None:
        await self.bot.lavalink.raw_handle_event_voice_server_update(
            event.state.guild_id,
            event.state.endpoint,
            event.state.token
        )

    async def on_ready_callback(self, _: ReadyEvent) -> None:
        builder = (
            LavalinkBuilder(
                self.bot.client_id, getenv("TOKEN")
            )
            .set_host("127.0.0.1")
            .set_port(8081)
            .set_password("your_lava_token")
            .set_start_gateway(False)
        )

        event_handler = type("EventHandler", (), {})
        lava_client = await builder.build(event_handler)

        self.bot.lavalink = lava_client

    async def join_callback(self, ctx: InteractionContext) -> None:
        guild_id = ctx.interaction.guild_id
        voice_state = self.bot.cache.get_voice_state(guild_id, ctx.author.id)
        channel_id = voice_state.channel_id

        await self.bot.gateway.voice_connect(guild_id=guild_id, channel_id=channel_id)
        await ctx.interaction.respond(content=f"Connected to <#{channel_id}>")
        connection = await self.bot.lavalink.wait_for_full_connection_info_insert(guild_id)

        await self.bot.lavalink.create_session(connection)

    async def play_callback(self, ctx: InteractionContext) -> None:
        query = await ctx.get_option("query")
        auto_search = await self.bot.lavalink.auto_search_tracks(" ".join(query))
        track = auto_search.tracks[0]

        await self.bot.lavalink.play(ctx.interaction.guild_id, track).requester(ctx.author.id).queue()
        await ctx.interaction.respond(content=f"Now playing **{track.info.title}**")
