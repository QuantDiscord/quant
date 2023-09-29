from datetime import datetime

from dispy.data.gateway.snowflake import Snowflake


def iso_to_datetime(time: str = None):
    if time is None:
        return

    return datetime.fromisoformat(time)


def snowflake_to_int(data: str = None) -> int:
    if data is None or not isinstance(data, (str, bytes, int)):
        return 0

    return int(data)


def execute_converters(cls, fields):
    results = []
    for field in fields:
        if field.converter is not None:
            results.append(field)
            continue
        if field.type in {datetime, 'datetime'}:
            converter = (
                lambda argument: iso_to_datetime(argument)
                if argument is not None else argument
            )
        elif field.type in {int, 'int'} or field.type in {Snowflake, "Snowflake"}:
            converter = snowflake_to_int
        else:
            converter = None
        results.append(field.evolve(converter=converter))

    return results
