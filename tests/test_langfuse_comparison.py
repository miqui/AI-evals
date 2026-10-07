"""Offline tests for llm/python/eval_langfuse_comparison.py (no keys, no network)."""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("langfuse")

PATH = Path(__file__).resolve().parents[1] / "llm" / "python" / "eval_langfuse_comparison.py"


@pytest.fixture
def module():
    spec = importlib.util.spec_from_file_location("eval_langfuse_comparison", PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_includes_expected(module):
    assert (
        module.includes_expected(input="q", output="It is Paris.", expected_output="paris").value
        == 1.0
    )
    assert module.includes_expected(input="q", output="Rome", expected_output="Paris").value == 0.0


def test_run_comparison_with_fake_model(module):
    answers = {d["input"]: d["expected_output"] for d in module.DATA}

    class FakeResult:
        def __init__(self, model):
            self.model = model

    # Stand-in client: runs the task + evaluators locally, as run_experiment would.
    class FakeLangfuse:
        def run_experiment(self, *, data, task, evaluators, **_):
            class Item:
                def __init__(self, evals):
                    self.evaluations = evals

            class Result:
                item_results = []

            result = Result()
            for d in data:
                out = task(item=d)
                result.item_results.append(
                    Item(
                        [
                            e(input=d["input"], output=out, expected_output=d["expected_output"])
                            for e in evaluators
                        ]
                    )
                )
            return result

        def flush(self):
            pass

    def call_model(model, question):
        return answers[question] if model == "good" else "no idea"

    means = module.run_comparison(FakeLangfuse(), models=["good", "bad"], call_model=call_model)
    assert means == {"good": 1.0, "bad": 0.0}
