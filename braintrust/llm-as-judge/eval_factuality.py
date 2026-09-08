"""Pre-built autoevals factuality scorer example.

Uses autoevals.Factuality, a battle-tested LLM-as-a-judge scorer that rates
how factual the task output is relative to the expected answer:
https://www.braintrust.dev/docs/evaluate/autoevals

All model traffic is Anthropic:
- Task calls use the `anthropic` SDK directly (ANTHROPIC_API_KEY).
- The judge runs via the Braintrust AI Gateway (BRAINTRUST_API_KEY), which
  requires an Anthropic provider key configured in the Braintrust org
  (one-time).

Requires ANTHROPIC_API_KEY and BRAINTRUST_API_KEY.
"""

from anthropic import Anthropic
from autoevals import Factuality

from braintrust import Eval

client = Anthropic()

JUDGE_MODEL = "claude-sonnet-4-5"

CAPITALS_DATASET = [
    {
        "input": "What is the capital of France?",
        "expected": "Paris",
    },
    {
        "input": "What is the capital of Japan?",
        "expected": "Tokyo",
    },
    {
        "input": "Who wrote the novel 'Pride and Prejudice'?",
        "expected": "Jane Austen",
    },
]


def task(input: str) -> str:
    """Answer a short trivia question."""
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=128,
        system="Answer the question concisely and factually.",
        messages=[{"role": "user", "content": input}],
    )
    return response.content[0].text


if __name__ == "__main__":
    Eval(
        "Trivia Factuality",
        data=CAPITALS_DATASET,
        task=task,
        scores=[Factuality(model=JUDGE_MODEL)],
        metadata={
            "model": "claude-sonnet-4-5",
        },
    )
