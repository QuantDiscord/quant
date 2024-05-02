"""
MIT License

Copyright (c) 2024 MagM1go

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import inspect
from typing import Dict, List, TypeVar, Callable, Set, overload

from quant.impl.events.types import EventTypes
from quant.entities.factory.event_factory import EventFactory, EventT

EventNameT = TypeVar("EventNameT", bound=str)


class EventController:
    def __init__(self, factory: EventFactory) -> None:
        self.factory = factory
        self._builtin_events = {
            EventTypes.READY_EVENT: self.factory.deserialize_ready_event,
            EventTypes.GUILD_CREATE: self.factory.deserialize_guild_create_event,
            EventTypes.INTERACTION_CREATE: self.factory.deserialize_interaction_event,
            EventTypes.MESSAGE_CREATE: self.factory.deserialize_message_create_event,
            EventTypes.MESSAGE_DELETE: self.factory.deserialize_message_delete_event,
            EventTypes.MESSAGE_UPDATE: self.factory.deserialize_message_edit_event,
            EventTypes.VOICE_STATE_UPDATE: self.factory.deserialize_voice_state_update_event,
            EventTypes.VOICE_SERVER_UPDATE: self.factory.deserialize_voice_server_update_event,
            EventTypes.CHANNEL_CREATE: self.factory.entity_factory.deserialize_channel,
            EventTypes.GUILD_MEMBER_ADD: self.factory.deserialize_guild_member_add_event,
            EventTypes.GUILD_MEMBER_REMOVE: self.factory.deserialize_guild_member_remove_event
        }

        event_func_prefix = "when_"

        for event_name, callback in self._builtin_events.items():
            setattr(self, event_func_prefix + event_name.lower(), callback)

        self.available: List[str] = [
            member[0][len(event_func_prefix):].upper()
            for member in inspect.getmembers(self)
            if member[0].startswith(event_func_prefix)
        ]

    @overload
    async def dispatch(self, event: EventT) -> None:
        ...

    @overload
    async def dispatch(self, event_name: str, details: Dict) -> None:
        ...

    async def dispatch(self, *args) -> None:
        if len(args) == 1:
            event = args[0]
            event_callbacks = self.factory.added_listeners.get(type(event))

            if event_callbacks is not None:
                for event_callback in event_callbacks:
                    await event_callback(event)

            if event is not None:
                await event.call()

        if len(args) == 2:
            event_name, details = args
            if event_name not in self.available:
                return

            event = getattr(self, 'when_' + event_name.lower())
            await self.dispatch(event(details))
