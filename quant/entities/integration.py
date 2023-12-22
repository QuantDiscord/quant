import enum
from datetime import datetime

import attrs

from .snowflake import Snowflake
from .model import BaseModel
from .user import User
from quant.utils.attrs_extensions import execute_converters, iso_to_datetime


class IntegrationExpireBehaviours(enum.Enum):
    NONE = -1
    REMOVE_ROLE = 0
    KICK = 1


@attrs.define
class IntegrationAccountObject(BaseModel):
    account_id: str = attrs.field(alias="id", default=None)
    name: str = attrs.field(default=None)


@attrs.define
class IntegrationApplicationObject(BaseModel):
    application_id: Snowflake = attrs.field(default=None)
    name: str = attrs.field(default=None)
    icon: str | None = attrs.field(default=None)
    description: str = attrs.field(default=None)
    bot: User | None = attrs.field(default=None, converter=User.as_dict)


@attrs.define(kw_only=True, field_transformer=execute_converters)
class Integration:
    integration_id: Snowflake = attrs.field(alias="id", default=0)
    integration_name: str = attrs.field(default=None, alias="name")
    integration_type: str = attrs.field(default=None, alias="type")
    enabled: bool = attrs.field(default=False)
    syncing: bool = attrs.field(default=False)
    role_id: Snowflake = attrs.field(default=0)
    enable_emoticons: bool = attrs.field(default=False)
    expire_behaviour: IntegrationExpireBehaviours = attrs.field(
        default=IntegrationExpireBehaviours.NONE, converter=IntegrationExpireBehaviours
    )
    expire_grace_period: int = attrs.field(default=0)
    user: User = attrs.field(default=None, converter=User.as_dict)
    account: IntegrationAccountObject = attrs.field(default=None, converter=IntegrationAccountObject.as_dict)
    synced_at: datetime = attrs.field(default=None, converter=iso_to_datetime)
    subscriber_count: int = attrs.field(default=0)
    revoked: bool = attrs.field(default=False)
    application: IntegrationApplicationObject = attrs.field(
        default=None, converter=IntegrationApplicationObject.as_dict
    )
