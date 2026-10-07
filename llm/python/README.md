# Model comparison — Python (Inspect AI)

Standalone: no dependency on `llm/node/`.

```bash
pip install -e '.[llm]'          # from the repo root
export ANTHROPIC_API_KEY=...

inspect eval llm/python/eval_model_comparison.py \
  --model anthropic/claude-haiku-4-5-20251001,anthropic/claude-sonnet-5-5,anthropic/claude-opus-5-5
inspect view                      # compare runs in the log viewer
```

Offline smoke run (used by tests/CI, no key needed):

```bash
inspect eval llm/python/eval_model_comparison.py --model mockllm/model
```

Edit `SAMPLES` in `eval_model_comparison.py` to change the dataset; swap
`includes()` for another scorer (`match`, `model_graded_qa`, ...) as needed.

## Langfuse experiments

`eval_langfuse_comparison.py` runs the same questions against each model as a
separate Langfuse experiment run (traced, scored, comparable in the UI):

```bash
export ANTHROPIC_API_KEY=... LANGFUSE_PUBLIC_KEY=... LANGFUSE_SECRET_KEY=...
python llm/python/eval_langfuse_comparison.py
```

Offline tests (`tests/test_langfuse_comparison.py`) use a fake client and model.
