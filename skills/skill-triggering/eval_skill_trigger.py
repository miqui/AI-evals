"""Skill-triggering eval: does Claude Code pick the right skill for a prompt?

Each case lists the skill expected to fire (or None for a negative case that
should fire no skill). The scorer is deterministic: it inspects the Skill
tool calls in the headless run, so no judge model is needed.

Runs against the project skills in this repo's `.claude/skills/`.
Requires the `claude` CLI (logged in) and BRAINTRUST_API_KEY.
"""

from pathlib import Path
from typing import Any

from runner import parse_skill_calls, run_claude

from braintrust import Eval

REPO_ROOT = Path(__file__).resolve().parents[2]

DATASET = [
    {
        "input": "openspec propose a change that adds a models/ topic for LLM comparison evals",
        "expected": "openspec-propose",
    },
    {
        "input": "I want to describe a feature and get a proposal, design and tasks for it",
        "expected": "openspec-propose",
    },
    {"input": "What is the capital of France?", "expected": None},
    {"input": "Rename the variable `x` to `count` in a Python snippet: x = 1", "expected": None},
]


def task(input: str) -> list[str]:
    return parse_skill_calls(run_claude(input, cwd=REPO_ROOT))


def skill_trigger(*, output: list[str], expected: str | None, **_: Any) -> float:
    """1.0 if the expected skill fired (or no skill fired for a negative case)."""
    if expected is None:
        return 1.0 if not output else 0.0
    return 1.0 if expected in output else 0.0


if __name__ == "__main__":
    Eval(
        "Skill Triggering",
        data=DATASET,
        task=task,
        scores=[skill_trigger],
    )
