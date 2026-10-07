"""Offline tests for the skill-triggering eval helpers (no claude/LLM calls)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "skill-triggering"))

from eval_skill_trigger import skill_trigger  # noqa: E402
from runner import parse_skill_calls  # noqa: E402


def _event(*blocks: dict) -> str:
    return json.dumps({"type": "assistant", "message": {"content": list(blocks)}})


def test_parse_skill_calls():
    stream = "\n".join(
        [
            json.dumps({"type": "system"}),
            _event({"type": "text", "text": "hi"}),
            _event({"type": "tool_use", "name": "Skill", "input": {"skill": "openspec-propose"}}),
            _event({"type": "tool_use", "name": "Read", "input": {}}),
            "not json",
        ]
    )
    assert parse_skill_calls(stream) == ["openspec-propose"]


def test_skill_trigger_scores():
    assert skill_trigger(output=["a"], expected="a") == 1.0
    assert skill_trigger(output=[], expected="a") == 0.0
    assert skill_trigger(output=[], expected=None) == 1.0
    assert skill_trigger(output=["a"], expected=None) == 0.0
