from __future__ import annotations as _

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot

from quant import SlashCommand, SlashSubCommand, ReadyEvent, VoiceServerUpdateEvent, VoiceStateUpdateEvent

from music import MusicModule


def register_components(bot: Bot) -> None:
    music = MusicModule(bot=bot)

    commands = [
        SlashCommand(name="music", description="I like music", options=[
            SlashSubCommand(name="join", description="Join a voice")
                .set_callback(music.join_callback),
            SlashSubCommand(name="play", description="Play music!")
                .set_callback(music.play_callback)
        ])
    ]
    events = {
        ReadyEvent: music.on_ready_callback,
        VoiceStateUpdateEvent: music.on_voice_state_update,
        VoiceServerUpdateEvent: music.on_voice_server_update
    }

    bot.add_slash_command(commands)

    for event_type, callback in events.items():
        bot.add_listener(event_type, callback)
