"""LLM-as-a-judge classifier example.

Uses autoevals.LLMClassifier to judge whether a task's output correctly
identifies a movie from its description. Adapted from Braintrust's docs:
https://www.braintrust.dev/docs/evaluate/llm-as-a-judge

All model traffic is Anthropic:
- Task calls use the `anthropic` SDK directly (ANTHROPIC_API_KEY).
- Judge scorers use `model="claude-sonnet-4-5"`; autoevals routes these
  through the Braintrust AI Gateway (BRAINTRUST_API_KEY), which requires an
  Anthropic provider key configured in the Braintrust org (one-time).

Requires ANTHROPIC_API_KEY and BRAINTRUST_API_KEY.
"""

from anthropic import Anthropic
from autoevals import LLMClassifier

from braintrust import Eval

client = Anthropic()

JUDGE_MODEL = "claude-sonnet-4-5"

MOVIE_DATASET = [
    {
        "input": "A detective investigates a series of murders based on the seven deadly sins.",
        "expected": "Se7en",
    },
    {
        "input": (
            "A thief who steals corporate secrets through the use of dream-sharing "
            "technology is given the inverse task of planting an idea into the mind of a C.E.O."
        ),
        "expected": "Inception",
    },
    {"input": "The capital of France is?", "expected": "Pariz"},
]


def task(input: str) -> str:
    """Ask the model to identify the movie from a plot description."""
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=64,
        system="Based on the following description, identify the movie. "
        "Reply with only the movie title.",
        messages=[{"role": "user", "content": input}],
    )
    return response.content[0].text


correctness_scorer = LLMClassifier(
    name="Correctness",
    prompt_template="""You are evaluating a movie-identification task.

Output (model's answer): {{output}}
Expected (correct movie): {{expected}}

Does the output correctly identify the same movie as the expected answer?
Consider alternate titles (e.g. "Harry Potter 1" vs
"Harry Potter and the Sorcerer's Stone") as correct.

Return only "correct" if the output is the right movie (exact or equivalent title).
Return only "incorrect" otherwise.""",
    choice_scores={
        "correct": 1,
        "incorrect": 0,
    },
    model=JUDGE_MODEL,
)


if __name__ == "__main__":
    Eval(
        "Movie Matcher",
        data=MOVIE_DATASET,
        task=task,
        scores=[correctness_scorer],
    )
