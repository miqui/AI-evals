"""Model comparison with Langfuse experiments: one run per model, same data.

Each model gets its own experiment run, so runs appear side by side in the
Langfuse UI with full traces and scores. Anthropic calls are traced via the
OpenTelemetry-based Langfuse SDK (`@observe`).

    python llm/python/eval_langfuse_comparison.py

Requires ANTHROPIC_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
(and LANGFUSE_HOST/LANGFUSE_BASE_URL for non-default regions or self-hosting).
"""

from collections.abc import Callable
from typing import Any

from langfuse import Evaluation, Langfuse, observe

MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-5-5",
    "claude-opus-5-5",
]

SYSTEM = "Answer with only the answer, no explanation."

DATA = [
    {"input": "What is the capital of France?", "expected_output": "Paris"},
    {
        "input": "Which movie features a detective hunting a killer using the seven deadly sins?",
        "expected_output": "Se7en",
    },
    {"input": "What is 17 * 3?", "expected_output": "51"},
    {"input": "What is the chemical symbol for gold?", "expected_output": "Au"},
    {"input": "Who wrote the novel '1984'?", "expected_output": "Orwell"},
]


def includes_expected(*, input: Any, output: str, expected_output: str, **_: Any) -> Evaluation:
    """Deterministic scorer: case-insensitive substring match."""
    hit = expected_output.lower() in (output or "").lower()
    return Evaluation(name="includes", value=1.0 if hit else 0.0)


def anthropic_call(model: str, question: str) -> str:
    from anthropic import Anthropic

    response = Anthropic().messages.create(
        model=model,
        max_tokens=64,
        system=SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def run_comparison(
    langfuse: Langfuse,
    models: list[str] = MODELS,
    call_model: Callable[[str, str], str] = anthropic_call,
) -> dict[str, float]:
    """Run one experiment per model; return mean `includes` score per model."""
    means: dict[str, float] = {}
    for model in models:

        @observe(name=f"answer[{model}]")
        def task(*, item: Any, _model: str = model, **_: Any) -> str:
            question = item["input"] if isinstance(item, dict) else item.input
            return call_model(_model, question)

        result = langfuse.run_experiment(
            name="Model comparison",
            run_name=f"model-comparison / {model}",
            description=f"Same {len(DATA)} questions, model={model}",
            data=DATA,
            task=task,
            evaluators=[includes_expected],
            metadata={"model": model},
        )
        scores = [
            e.value
            for r in result.item_results
            for e in r.evaluations
            if e.name == "includes" and isinstance(e.value, int | float)
        ]
        means[model] = sum(scores) / len(scores) if scores else 0.0
    langfuse.flush()
    return means


if __name__ == "__main__":
    for model, mean in run_comparison(Langfuse()).items():
        print(f"{model}: {mean:.2f}")
