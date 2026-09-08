"""Trace-level LLM-as-a-judge example: conversation coherence.

Judges the coherence of a full multi-turn support conversation, mapping a
letter grade (A/B/C) to numeric scores (1 / 0.6 / 0). Adapted from
Braintrust's docs:
https://www.braintrust.dev/docs/evaluate/llm-as-a-judge#score-traces

All model traffic is Anthropic:
- Task calls use the `anthropic` SDK (wrapped for tracing) with
  ANTHROPIC_API_KEY.
- The judge call uses the `anthropic` SDK via the Braintrust AI Gateway
  (BRAINTRUST_API_KEY), which requires an Anthropic provider key configured
  in the Braintrust org (one-time).

Requires ANTHROPIC_API_KEY and BRAINTRUST_API_KEY.
"""

import os
from typing import Any

from anthropic import Anthropic

from braintrust import Eval, wrap_anthropic

client = Anthropic()
wrapped_client = wrap_anthropic(Anthropic())

JUDGE_MODEL = "claude-sonnet-4-5"

SUPPORT_DATASET = [
    {"input": "My order hasn't arrived yet. Order #12345."},
    {"input": "I need help resetting my password."},
]

CHOICE_SCORES = {"A": 1.0, "B": 0.6, "C": 0.0}


def call_llm(messages: list[dict[str, str]]) -> str:
    """Traced LLM call so the full conversation is captured on the trace."""
    system = next(m["content"] for m in messages if m["role"] == "system")
    turns = [m for m in messages if m["role"] != "system"]
    response = wrapped_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=system,
        messages=turns,  # type: ignore[arg-type]
    )
    return response.content[0].text


def support_task(input: str) -> str:
    """Simulate a three-turn support conversation and return the last reply."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": "You are a helpful customer support agent."},
        {"role": "user", "content": input},
    ]
    response1 = call_llm(messages)
    messages.append({"role": "assistant", "content": response1})
    messages.append({"role": "user", "content": "Can you provide more details?"})
    response2 = call_llm(messages)
    messages.append({"role": "assistant", "content": response2})
    messages.append({"role": "user", "content": "Thank you for your help!"})
    response3 = call_llm(messages)
    return response3


def conversation_coherence(**kwargs: Any) -> dict[str, Any] | None:
    """Judge the whole conversation output for coherence (A/B/C -> score).

    In this offline-eval form the task output is the final reply; the judge
    call is routed through the Braintrust AI Gateway with an Anthropic model.
    """
    output = kwargs.get("output") or ""
    if not output:
        return None
    judge = Anthropic(
        api_key=os.environ["BRAINTRUST_API_KEY"],
        base_url=os.environ.get(
            "BRAINTRUST_AI_GATEWAY_URL",
            "https://api.braintrust.dev/v1/ai_gateway",
        ),
        default_headers={"x-bt-use-cache": "false"},
    )
    response = judge.messages.create(
        model=JUDGE_MODEL,
        max_tokens=16,
        messages=[
            {
                "role": "user",
                "content": f"""Evaluate the coherence of this customer support conversation:

{output}

Rate the conversation coherence:
- "A" for highly coherent with natural flow and consistent context
- "B" for mostly coherent with minor gaps or context issues
- "C" for incoherent, disjointed, or lost context

Return only the letter (A, B, or C).""",
            },
        ],
    )
    rating = response.content[0].text.strip().upper()[:1]
    score = CHOICE_SCORES.get(rating, 0.0)
    return {
        "name": "Conversation coherence",
        "score": score,
        "metadata": {"rating": rating},
    }


if __name__ == "__main__":
    Eval(
        "Support Conversation Quality",
        data=SUPPORT_DATASET,
        task=support_task,
        scores=[conversation_coherence],
    )
