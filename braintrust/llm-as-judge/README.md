# LLM-as-a-Judge with Braintrust (Python)

Reference: [LLM-as-a-judge scorers and classifiers — Braintrust docs](https://www.braintrust.dev/docs/evaluate/llm-as-a-judge)

LLM-as-a-judge scorers use a language model to evaluate outputs based on
natural language criteria. A **scorer** returns a numeric score between 0 and
1; a **classifier** returns a categorical label. They are best for subjective
judgments (tone, helpfulness, coherence) that are hard to encode
deterministically.

## Concepts covered

| Script | What it demonstrates |
|--------|----------------------|
| `eval_llm_classifier.py` | `autoevals.LLMClassifier` — judge prompt template with `choice_scores` (`correct`/`incorrect`), run as an inline SDK eval |
| `eval_factuality.py` | `autoevals.Factuality` — pre-built factuality scorer comparing output against expected |
| `eval_trace_coherence.py` | Trace-level scorer — judge a full multi-turn support conversation's coherence, mapping a letter grade (A/B/C) to scores (1 / 0.6 / 0) |

All scripts use **Anthropic models end to end** (no OpenAI key needed):

- Task calls: `anthropic` SDK with `ANTHROPIC_API_KEY`
- Judge scorers (`LLMClassifier`, `Factuality`): `model="claude-sonnet-4-5"`
  routed through the **Braintrust AI Gateway** with `BRAINTRUST_API_KEY`
- One-time prerequisite: an Anthropic provider key configured in the
  Braintrust org settings so the Gateway can proxy `claude-*` models

## Prerequisites

```bash
pip install -e '.[dev]'   # from the repo root
export ANTHROPIC_API_KEY=...    # task model calls
export BRAINTRUST_API_KEY=...   # Braintrust eval runs + judge routing
```

## Running

```bash
python braintrust/llm-as-judge/eval_llm_classifier.py
python braintrust/llm-as-judge/eval_factuality.py
python braintrust/llm-as-judge/eval_trace_coherence.py
```

Each run creates an experiment snapshot in your Braintrust project and prints
a link plus summary metrics. The `bt eval` CLI can also run these files.

## Notes

- These scripts call real models and are **not** run in CI (no API keys
  there); CI covers linting and a deterministic no-LLM smoke test.
- Judge prompts use `{{input}}`, `{{output}}`, `{{expected}}`, `{{metadata}}`
  template variables per Braintrust's span-scorer contract.
- To push scorers for team-wide/production use, see Braintrust's CLI scorer
  push workflow (`bt scorers`).
