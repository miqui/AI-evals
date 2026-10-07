"""Offline smoke test for llm/python: runs the Inspect task on the mock model."""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("inspect_ai")
from inspect_ai import eval as inspect_eval  # noqa: E402

PATH = Path(__file__).resolve().parents[1] / "llm" / "python" / "eval_model_comparison.py"


def test_model_comparison_runs_on_mock_model(tmp_path):
    spec = importlib.util.spec_from_file_location("eval_model_comparison", PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    logs = inspect_eval(
        module.model_comparison(),
        model="mockllm/model",
        log_dir=str(tmp_path),
        log_format="json",
        display="none",
    )
    assert logs[0].status == "success"
    assert logs[0].results is not None
    assert logs[0].results.total_samples == len(module.SAMPLES)
