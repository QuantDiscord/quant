from typing import List, Any
from datetime import datetime

import attrs

from quant.entities.snowflake import Snowflake


def iso_to_datetime(time: str = None) -> datetime | None:
    if time is None:
        return

    return datetime.fromisoformat(time)


def int_converter(data: Any = None) -> int | Snowflake:
    check = isinstance(data, str)
    if data is None or not check:
        return 0

    if check:
        return Snowflake(int(data))

    return int(data)


def to_snowflake(data: str = None) -> Snowflake:
    return Snowflake(int(data))


def execute_converters(_, fields: List[attrs.Attribute]) -> List[attrs.Attribute]:
    converters = {
        datetime: iso_to_datetime,
        'datetime': iso_to_datetime,
        int: int_converter,
        'int': int_converter,
        Snowflake: int_converter,
        'Snowflake': int_converter
    }

    results = []
    for field in fields:
        converter = converters.get(field.type)
        results.append(
            field if field.converter is not None
            else field.evolve(converter=converter)
        )

    return results
