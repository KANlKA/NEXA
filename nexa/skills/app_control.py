"""
app_control.py

Opens macOS applications via AppleScript (osascript). This is a small
preview of Phase 3's app control skill — we need at least one REAL skill
(not just the ping test) to prove the orchestrator actually routes
commands to the right place with the right params.
"""

import re
import subprocess
from nexa.skills.base import Skill, SkillResult

# Matches "open X", "launch X", "start X" — capturing the app name.
# Anchored and conservative on purpose: e.g. "open my mind to new ideas"
# would NOT match cleanly as a sensible app name, but common phrasing does.
_OPEN_APP_PATTERN = re.compile(r"^(?:open|launch|start)\s+(.+)$", re.IGNORECASE)


class OpenAppSkill(Skill):
    name = "open_app"
    description = (
        'Opens/launches a macOS application by name. '
        'params: {"app_name": "<exact app name, e.g. Chrome, Spotify, Terminal, Visual Studio Code>"}'
    )

    def try_fast_match(self, text: str) -> dict | None:
        match = _OPEN_APP_PATTERN.match(text.strip())
        if match:
            app_name = match.group(1).strip().rstrip("?.!")
            return {"app_name": app_name}
        return None

    async def execute(self, params: dict, context: dict) -> SkillResult:
        app_name = params.get("app_name")
        if not app_name:
            return SkillResult(success=False, spoken_response="I didn't catch which app to open.")

        try:
            subprocess.run(
                ["osascript", "-e", f'tell application "{app_name}" to activate'],
                check=True,
                capture_output=True,
            )
            return SkillResult(success=True, spoken_response=f"Opening {app_name}.")
        except subprocess.CalledProcessError:
            return SkillResult(success=False, spoken_response=f"I couldn't find an app called {app_name}.")
