import attrs

from dispy.data.activities.acitivity_status import ActivityStatus
from dispy.data.activities.activity_types import ActivityType


@attrs.define
class Activity:
    name: str = attrs.field()
    url: str | None = attrs.field(default=None)
    type: ActivityType = attrs.field(default=ActivityType.GAME)


@attrs.define
class ActivityBuilder:
    activity: Activity | None = attrs.field(default=None)
    status: ActivityStatus | None = attrs.field(default=None)
    since: int | None = attrs.field(default=None)
    afk: bool = attrs.field(default=False)
