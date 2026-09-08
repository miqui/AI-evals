# AI-evals

A collection of AI evaluation concerns and topics, organized by subdirectory.
Each subdirectory is a self-contained topic with its own README, runnable
examples, and (where applicable) CI coverage.

## Layout

| Path | Topic |
|------|-------|
| `braintrust/llm-as-judge/` | LLM-as-a-judge scorers and classifiers with the Braintrust Python SDK |

## Topics

### `braintrust/llm-as-judge/`

LLM-as-a-judge evaluation using [Braintrust](https://www.braintrust.dev/) and
its Python SDKs (`braintrust`, `autoevals`, `openai`). Covers:

- `LLMClassifier` — judge prompt with choice scores (correct/incorrect)
- `Factuality` — pre-built autoevals factuality scorer
- Trace-level coherence scoring for multi-turn conversations

See [braintrust/llm-as-judge/README.md](braintrust/llm-as-judge/README.md)
for usage and prerequisites (API keys).

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

API keys are required only for the LLM-backed examples:

- `ANTHROPIC_API_KEY` — task model calls (Anthropic SDK)
- `BRAINTRUST_API_KEY` — Braintrust SDK eval runs + judge-model routing via
  the Braintrust AI Gateway

All model traffic in the examples uses Anthropic Claude models; no OpenAI
key is needed.

## CI

GitHub Actions runs on every pull request:

- `lint` — ruff check + format check
- `smoke` — deterministic no-LLM scorer test (no API keys needed)

LLM-backed eval scripts require credentials and run locally (or via a
manually dispatched, secret-gated job).
