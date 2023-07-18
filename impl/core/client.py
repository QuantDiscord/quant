import inspect
from typing import Coroutine, Callable, Any

from dispy.impl.core.gateway import Gateway
from dispy.data.intents import Intents
from dispy.impl.core.exceptions.library_exception import LibraryException
from dispy.impl.core.rest import DiscordREST
from dispy.impl.events.event import BaseEvent
from dispy.data.model import BaseModel
from dispy.data.activities.activity import ActivityBuilder


class Client:
    def __init__(
        self,
        token: str,
        intents: Intents,
        prefix: str = None,
        with_mobile_status: bool = False,
    ) -> None:
        self.token = token
        self.prefix = prefix
        self.intents = intents
        self.with_mobile_status = with_mobile_status
        self.gateway: Gateway = Gateway(token=token, intents=self.intents, mobile_status=self.with_mobile_status)
        self.rest = DiscordREST(self.gateway.token)
        self.cache = self.gateway.cache

    _Coroutine = Callable[..., Coroutine[Any, Any, Any]]

    async def run(self) -> None:
        BaseModel.set_client(self)
        await self.gateway.connect_ws()

    def set_activity(self, activity: ActivityBuilder) -> None:
        self.gateway.set_presence(
            activity=activity.activity,
            status=activity.status,
            since=activity.since,
            afk=activity.afk
        )

    def add_listener(self, event, coro: _Coroutine) -> None:
        if inspect.iscoroutine(coro):
            raise LibraryException("Callback function must be coroutine")

        if not issubclass(event, BaseEvent):
            raise LibraryException(f"Subclass of event {event} must be BaseEvent")

        self.gateway.add_event(event.API_EVENT_NAME, event, coro)
