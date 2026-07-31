"""
base.py

Defines the contract every skill (AppControl, Coding, Browser, Memory...)
must follow. This is what lets the orchestrator route ANY command to ANY
skill without needing an if/elif chain that knows about every feature.

If you've done OOP before: this is an abstract base class (ABC).
It can't be instantiated directly — it just defines "if you want to be
a Skill, you MUST implement these methods."
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillResult:
    """What every skill hands back to the orchestrator."""
    success: bool
    spoken_response: str = ""      # what Nexa should say out loud, e.g. "Done."
    data: dict = field(default_factory=dict)   # any structured data (e.g. file paths found)
    cacheable: bool = False        # can this exact result be reused for a repeat command?


class Skill(ABC):
    # Every skill names itself — used for logging and routing decisions.
    name: str = "unnamed_skill"

    # Plain-English description of what this skill does and what params it
    # expects, e.g. 'Opens a macOS app. params: {"app_name": "Chrome"}'.
    # This is what gets shown to the LLM so it knows what's actually
    # available to call — without this, the model invents skill names
    # that don't exist.
    description: str = ""

    @abstractmethod
    async def execute(self, params: dict, context: dict) -> SkillResult:
        """
        params:  structured arguments the orchestrator extracted from your command
                  e.g. {"app_name": "Chrome"} for "open Chrome"
        context: live state — current app, project, selected code, etc.
                  (built out properly in a later phase; empty dict for now)
        """
        raise NotImplementedError

    def try_fast_match(self, text: str) -> dict | None:
        """
        Optional "Tier 0" check: can this skill handle `text` with a cheap,
        deterministic pattern match — no LLM call needed?

        Return a params dict if yes (execute() runs immediately with these
        params). Return None if this skill can't confidently handle it,
        deferring to the LLM (Tier 1) instead.

        Default: never fast-matches. Skills opt in by overriding this.
        Keep these patterns CONSERVATIVE — a wrong fast match is worse than
        falling back to the (slower but smarter) LLM.
        """
        return None

    def can_handle(self, intent: str) -> bool:
        """
        Cheap check: does this skill handle a given intent name?
        Default implementation; skills can override with smarter matching.
        """
        return intent == self.name
