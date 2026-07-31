"""
ping.py

A throwaway skill just to prove the plumbing works before we build
anything real. Once app_control.py etc. exist in Phase 3, this file
can be deleted.
"""

from nexa.skills.base import Skill, SkillResult


class PingSkill(Skill):
    name = "ping"
    description = "Checks that Nexa is running. No params needed. Use for commands like 'are you there' or 'ping'."

    # A small, fixed set of exact phrasings — deliberately narrow. If it's
    # not one of these, we'd rather let the LLM interpret it than risk a
    # wrong fast match.
    _FAST_PHRASES = {"are you there", "ping", "you there", "hey are you there", "you awake"}

    def try_fast_match(self, text: str) -> dict | None:
        normalized = text.strip().lower().rstrip("?.!")
        if normalized in self._FAST_PHRASES:
            return {}
        return None

    async def execute(self, params: dict, context: dict) -> SkillResult:
        return SkillResult(
            success=True,
            spoken_response="Pong. Nexa is alive.",
            cacheable=False,
        )
