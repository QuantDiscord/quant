async def dispatch(gateway_client, received_event_type, **kwargs) -> None:
    cache_manager = gateway_client.cache
    event_list = gateway_client.event_list()

    for event_callback, event_data in event_list.items():
        if received_event_type not in event_data:
            continue

        event_class = event_data[received_event_type]()
        if hasattr(event_class, "process_event"):
            event_class.process_event(cache_manager, **kwargs)

        await event_callback(event_class)
