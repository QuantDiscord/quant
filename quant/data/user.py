from __future__ import annotations
_B=False
_A=None
from typing import Any
import attrs
from quant.data.model import BaseModel
from quant.data.gateway.snowflake import Snowflake
from quant.utils.attrs_extensions import execute_converters,int_converter
@attrs.define(field_transformer=execute_converters)
class User(BaseModel):
        username=attrs.field();user_id=attrs.field(alias='id',default=0,converter=int_converter);discriminator=attrs.field(default=_A);display_name=attrs.field(default=_A);global_name=attrs.field(default=_A);avatar=attrs.field(default=_A);is_bot=attrs.field(alias='bot',default=_B);is_system=attrs.field(alias='system',default=_B);mfa_enabled=attrs.field(default=_B);banner_hash=attrs.field(alias='banner',default=_A);accent_color=attrs.field(default=_A);banner_color=attrs.field(default=_A);avatar_decoration=attrs.field(default=_A);locale=attrs.field(default=_A);flags=attrs.field(default=0);premium_type=attrs.field(default=0);public_flags=attrs.field(default=0);avatar_decoration_data=attrs.field(default=_A);verified=attrs.field(default=_B);_email=attrs.field(default=_A,alias='email');_member=attrs.field(alias='member',default=_A)
        @classmethod
        def as_dict(A,data):
                if data is not _A:return A(**data)
        @classmethod
        def as_dict_iter(A,data):
                if data is not _A:return[A(**B)for B in data]