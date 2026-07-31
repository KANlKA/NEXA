from nexa.skills.base import Skill, SkillResult


class PingSkill(Skill):
    name = "ping"
    description = "Checks that Nexa is running. No params needed. Use for commands like 'are you there' or 'ping'."

    async def execute(self, params: dict, context: dict) -> SkillResult:
        return SkillResult(
            success=True,
            spoken_response="Pong. Nexa is alive.",
            cacheable=False,
        )
