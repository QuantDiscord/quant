from __future__ import annotations as _

from enum import Enum

from quant.utils.parser import clamp


class RGB:
    def __new__(cls, r: int, g: int, b: int) -> int:
        r, g, b = (
            clamp(r), clamp(g), clamp(b)
        )
        hex_string = f"0x{r:02x}{g:02x}{b:02x}"

        return int(hex_string, 16)


class Hex:
    def __new__(cls, value: str | int) -> int:
        if isinstance(value, int):
            return value

        if value.startswith("#"):
            value = value[1:]

        return int.from_bytes(bytes.fromhex(value), "big")


class Color:
    RED = 0xcc0000
    ORANGE = 0xff9900
    YELLOW = 0xffff00
    GREEN = 0x66ff00
    CYAN = 0x99ffff
    BLUE = 0x3399ff
    PURPLE = 0x990099

    def __new__(cls, *args):
        if len(args) == 1:
            return Hex(args[0])

        if len(args) == 3:
            return RGB(*args)

        raise ValueError("Can't convert to HEX or RGB.")
