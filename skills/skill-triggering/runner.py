"""Run a prompt through headless Claude Code and extract which skills it invoked.

`claude -p --output-format stream-json --verbose` emits one JSON event per line.
Assistant events carry `tool_use` content blocks; a skill invocation is a
`tool_use` named "Skill" whose input has a `skill` field.
"""

import json
import subprocess
from pathlib import Path


def parse_skill_calls(stream: str) -> list[str]:
    """Return skill names invoked, in order, from a stream-json transcript."""
    skills: list[str] = []
    for line in stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                skills.append(block.get("input", {}).get("skill", ""))
    return skills


def run_claude(prompt: str, cwd: Path, timeout: int = 180) -> str:
    """Run `claude -p` in `cwd` (so project skills load) and return the raw stream."""
    result = subprocess.run(
        [
            "claude",
            "-p",
            prompt,
            "--output-format",
            "stream-json",
            "--verbose",
            "--max-turns",
            "3",
            "--no-session-persistence",
            # Planning-only: we only care whether the skill is selected, so deny
            # file edits and shell to keep runs side-effect free.
            "--disallowedTools",
            "Edit",
            "Write",
            "Bash",
        ],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return result.stdout
