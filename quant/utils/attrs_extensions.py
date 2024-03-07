from datetime import datetime


def iso_to_datetime(time: str = None) -> datetime | None:
    if time is None:
        return

    return datetime.fromisoformat(time)
