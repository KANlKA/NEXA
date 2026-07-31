"""
orchestrator.py

The brain. Takes transcribed text, asks the LLM to choose which
REGISTERED skill should handle it (constrained to skills that actually
exist — see registry.py), executes that skill, and returns the result.

This is "Tier 1" (LLM-based routing) from the roadmap. Tier 0 (instant
regex shortcuts for common commands, no LLM round-trip) and Tier 2
(cloud fallback for anything the local model struggles with) get added
later, once we've proven this core routing loop is reliable.
"""

from nexa.llm import ask_structured
from nexa.registry import SkillRegistry
from nexa.skills.base import SkillResult

SYSTEM_PROMPT_TEMPLATE = """You are Nexa's command router. Given a transcribed voice command, decide which skill should handle it and what parameters to extract from the command.

Available skills:
{skills}

Respond with ONLY a JSON object, no other text, in this exact shape:
{{"skill": "<one of the exact skill names listed above>", "params": {{...}}}}

If nothing above matches the command, respond with exactly:
{{"skill": "none", "params": {{}}}}
"""


class Orchestrator:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    async def handle(self, text: str, context: dict | None = None) -> SkillResult:
        context = context or {}
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(skills=self.registry.describe_for_llm())

        try:
            decision = ask_structured(prompt=f'Command: "{text}"', system=system_prompt)
        except ValueError:
            # Model failed to return parseable JSON at all
            return SkillResult(success=False, spoken_response="I had trouble understanding that.")

        skill_name = decision.get("skill", "none")
        params = decision.get("params", {})

        if skill_name == "none":
            return SkillResult(success=False, spoken_response="I'm not sure how to do that yet.")

        skill = self.registry.get(skill_name)
        if skill is None:
            # The model hallucinated a skill name that isn't registered.
            # This should get rarer as the skill list grows and descriptions
            # improve, but we never want to silently pretend it worked.
            return SkillResult(
                success=False,
                spoken_response="I tried to do that, but I don't actually have that ability yet.",
            )

        return await skill.execute(params, context)
