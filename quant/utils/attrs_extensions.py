from typing import List
from datetime import datetime

import attrs

from quant.entities.snowflake import Snowflake


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
    converters = {
        datetime: lambda argument: iso_to_datetime(argument) if argument is not None else argument,
        'datetime': lambda argument: iso_to_datetime(argument) if argument is not None else argument,
        int: int_converter,
        'int': int_converter,
        Snowflake: int_converter,
        'Snowflake': int_converter
    }

    results = []
    for field in fields:
        if field.converter is not None:
            results.append(field)
            continue

        results.append(field.evolve(converter=converters.get(field.type)))

    return results
