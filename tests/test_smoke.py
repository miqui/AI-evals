"""Deterministic smoke test: no LLM calls, no API keys required.

Validates that the repo's core eval scaffolding is importable and that a
plain code scorer (exact match) computes expected scores. LLM-backed eval
scripts are exercised locally by the user, not in CI.

The eval scripts construct an Anthropic client at module import time, which
only requires a non-empty key env var (no network at import), so a dummy key
keeps these tests fully offline.
"""

import importlib.util
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[1] / "braintrust" / "llm-as-judge"


@pytest.fixture(autouse=True)
def _dummy_keys(monkeypatch):
    """Allow Anthropic() construction without real credentials; no calls made."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-dummy-key-not-real")
    monkeypatch.setenv("BRAINTRUST_API_KEY", "test-dummy-key-not-real")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_eval_scripts_import_without_llm_calls():
    """Scripts must import cleanly (module-level code must not call LLMs)."""
    for filename in ("eval_llm_classifier.py", "eval_factuality.py", "eval_trace_coherence.py"):
        module = _load_module(filename.replace(".py", "").replace("-", "_"), BASE / filename)
        assert module is not None


def test_exact_match_scorer():
    """A plain code scorer: deterministic, no judge model."""

    def exact_match(*, output: str, expected: str) -> float:
        return 1.0 if output.strip() == expected.strip() else 0.0

    assert exact_match(output="Se7en", expected="Se7en") == 1.0
    assert exact_match(output="se7en ", expected="Se7en") == 0.0


def test_coherence_choice_scores():
    module = _load_module("eval_trace_coherence", BASE / "eval_trace_coherence.py")
    assert module.CHOICE_SCORES == {"A": 1.0, "B": 0.6, "C": 0.0}
