"""
orchestrator.py

The brain. Takes transcribed text and routes it to a skill in one of two ways:

  Tier 0 (fast path): check every registered skill's try_fast_match() first.
  If one recognizes the command via simple pattern matching, run it
  immediately — no LLM call, near-instant response.

  Tier 1 (LLM routing): if no skill fast-matched, ask the local LLM to pick
  from the REGISTERED skills (constrained — see registry.py) and extract
  params. Slower, but handles phrasing Tier 0's simple patterns can't.

Tier 2 (cloud fallback for cases the local model struggles with) is a
future addition once we hit real cases that need it.
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

        # --- Tier 0: fast pattern matching, no LLM ---
        for skill in self.registry.all_skills():
            params = skill.try_fast_match(text)
            if params is not None:
                print(f"[Tier 0] Fast-matched '{skill.name}' — skipping LLM.")
                return await skill.execute(params, context)

        # --- Tier 1: LLM-based routing ---
        print("[Tier 1] No fast match — asking the LLM to route this.")
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
