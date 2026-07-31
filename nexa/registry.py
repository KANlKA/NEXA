"""
registry.py

Holds every skill Nexa knows about. Two jobs:
  1. Look up a skill by name when the orchestrator needs to run one
  2. Generate a description of ALL registered skills to hand to the LLM,
     so it can only pick from what actually exists — no more invented
     skill names like "open_browser" that don't map to real code.
"""

from nexa.skills.base import Skill


class SkillRegistry:
    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def all_skills(self) -> list[Skill]:
        return list(self._skills.values())

    def describe_for_llm(self) -> str:
        """Formats every registered skill as a line the LLM prompt can include."""
        lines = [f'- "{skill.name}": {skill.description}' for skill in self._skills.values()]
        return "\n".join(lines)
