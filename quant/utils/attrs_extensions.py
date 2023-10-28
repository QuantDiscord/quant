from typing import List
from datetime import datetime

import attrs

from quant.data.gateway.snowflake import Snowflake


def iso_to_datetime(time: str = None):
    if time is None:
        return

    return datetime.fromisoformat(time)


def int_converter(data: str = None) -> int | Snowflake:
    check = isinstance(data, (str, bytes, int))
    if data is None or not check:
        return 0

    if check:
        return Snowflake(int(data))

    return int(data)


def to_snowflake(data: str = None) -> int | Snowflake:
    return Snowflake(int(data))


def execute_converters(cls, fields: List[attrs.Attribute]):
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
            converter = int_converter
        else:
            converter = None
        results.append(field.evolve(converter=converter))

    return results
