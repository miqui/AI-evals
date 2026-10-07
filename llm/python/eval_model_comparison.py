"""Model comparison with Inspect AI: same dataset, same scorer, N models.

Run one model or several in one command; Inspect logs each run for `inspect view`:

    inspect eval llm/python/eval_model_comparison.py \
        --model anthropic/claude-haiku-4-5-20251001,anthropic/claude-sonnet-5-5

Offline smoke run (no API key): `--model mockllm/model`.
Requires ANTHROPIC_API_KEY for real runs.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate, system_message

SYSTEM = "Answer with only the answer, no explanation."

SAMPLES = [
    Sample(input="What is the capital of France?", target="Paris"),
    Sample(
        input="Which movie features a detective hunting a killer using the seven deadly sins?",
        target="Se7en",
    ),
    Sample(input="What is 17 * 3?", target="51"),
    Sample(input="What is the chemical symbol for gold?", target="Au"),
    Sample(input="Who wrote the novel '1984'?", target="Orwell"),
]


@task
def model_comparison() -> Task:
    return Task(
        dataset=MemoryDataset(SAMPLES),
        solver=[system_message(SYSTEM), generate()],
        scorer=includes(),
    )
