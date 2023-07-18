from datetime import datetime


def fromisoformat_extension(time: str = None):
    if time is None:
        return

    return datetime.fromisoformat(time)


def from_snowflake_to_int(data: str = None) -> int:
    if data is None or not isinstance(data, (str, bytes, int)):
        return 0

    return int(data)


def auto_converter(cls, fields):
    results = []
    for field in fields:
        if field.converter is not None:
            results.append(field)
            continue
        if field.type in {datetime, 'datetime'}:
            converter = (
                lambda argument: fromisoformat_extension(argument)
                if argument is not None else argument
            )
        elif field.type in {int, 'int'}:
            converter = (
                lambda argument: from_snowflake_to_int(argument)
                if argument is not None else argument
            )
        else:
            converter = None
        results.append(field.evolve(converter=converter))

    return results
