from typing import TypeVar, Callable, Coroutine, Any, Generic

ContextT = TypeVar("ContextT")
CoroutineT = TypeVar("CoroutineT", bound=Callable[..., Coroutine[Any, Any, Any]])


class CallbackBackend(Generic[ContextT]):
    async def callback(self, context: ContextT):
        pass

    callback_func = callback

    def set_callback(self, coro: CoroutineT):
        self.callback_func = coro
