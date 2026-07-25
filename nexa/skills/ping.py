from nexa.skills.base import Skill, SkillResult

class PingSkill(Skill):
    name = "ping"

    async def execute(self, params: dict, context: dict) -> SkillResult:
        return SkillResult(
            success=True,
            spoken_response="Pong. Nexa is alive.",
            cacheable=False,
        )