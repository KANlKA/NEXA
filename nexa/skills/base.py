#Defines the contract every skill (AppControl, Coding, Browser, Memory...) must follow. This is what lets the orchestrator route ANY command to ANY skill without needing an if/elif chain that knows about every feature.

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

    @abstractmethod
    async def execute(self, params: dict, context: dict) -> SkillResult:
        """
        params:  structured arguments the orchestrator extracted from your command
                  e.g. {"app_name": "Chrome"} for "open Chrome"
        context: live state — current app, project, selected code, etc.
                  (built out properly in a later phase; empty dict for now)
        """
        raise NotImplementedError

    def can_handle(self, intent: str) -> bool:
        """
        Cheap check: does this skill handle a given intent name?
        Default implementation; skills can override with smarter matching.
        """
        return intent == self.name
