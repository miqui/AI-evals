# Model comparison — Node (promptfoo)

Standalone: no dependency on `llm/python/`.

```bash
cd llm/node
npm install
export ANTHROPIC_API_KEY=...
npm run eval        # prompts x models x tests matrix
npm run view        # web UI to compare models
```

`npm run eval:smoke` runs an offline config with the `echo` provider (no key)
to verify the pipeline. Edit `tests.yaml` for cases and
`promptfooconfig.yaml` for models/prompts.

## Langfuse experiments

`langfuse-comparison.mjs` runs the same questions against each model as a
separate Langfuse experiment run (traced, scored, comparable in the UI):

```bash
export ANTHROPIC_API_KEY=... LANGFUSE_PUBLIC_KEY=... LANGFUSE_SECRET_KEY=...
npm run langfuse
npm test            # offline tests with a fake client and model
```
