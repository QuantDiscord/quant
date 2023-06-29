from dispy.impl.events.guild.message_events import MessageDeleteEvent
from dispy.impl.events.guild.message_events.message_edit_event import MessageEditEvent
from dispy.impl.events.guild.message_events.message_event import MessageEvent


async def dispatch(gateway_client, received_event_type, **kwargs) -> None:
    cache_manager = gateway_client.cache
    event_list = {value: key for key, value in gateway_client.event_list().items()}  # i'm stupid

    event_objects = [[event_callback, event_data] for event_callback, event_data in event_list.items()
                     if received_event_type in event_data]

    for event_object in event_objects:
        event_class = event_object[1][received_event_type]()
        event_callback = event_object[0]

        if isinstance(event_class, MessageEditEvent):
            message = cache_manager.get_message(int(kwargs.get("id")))
            if message is None:
                return

            event_class.previous_message = message

        event_class.build_event(**kwargs)

        if isinstance(event_class, MessageDeleteEvent):
            # author = cache_manager.get_user(int(kwargs.get("author")["id"]))
            message = cache_manager.get_message(int(kwargs.get("id")))
            if message is None:
                return

            event_class.message = message

        if isinstance(event_class, MessageEvent):
            cache_manager.add_cache_message(event_class.message)

        await event_callback(event_class)

# СУКА Я ЧУТЬ НЕ ПОВЕСИЛСЯ НАХУЙ, ПОКА ПИСАЛ ЭТО
# Всем любви.
# Я правда не хотел писать такой код, меня заставили. Правда.
