from typing import Dict, Any

import attrs

from quant.data.guild.members.member import GuildMember


class EntityFactory:
    def serialize_member_object(self, member: GuildMember) -> Dict[str, Any]:
        return attrs.asdict(member)
