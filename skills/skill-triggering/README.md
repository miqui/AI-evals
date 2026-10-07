# Skill triggering evals

Checks that Claude Code selects the right skill for a prompt, and stays quiet
when no skill applies. The task runs `claude -p --output-format stream-json`
from the repo root (so `.claude/skills/` loads) and the scorer reads the
`Skill` tool calls from the transcript. Deterministic: no judge model.

```bash
python skills/skill-triggering/eval_skill_trigger.py
```

Requires the `claude` CLI and `BRAINTRUST_API_KEY`. Runs use real model calls,
so they are not part of CI; the transcript parser and scorer are covered by
offline tests in `tests/test_skills.py`.

To eval a new skill, add positive cases (expected = skill name) and negative
cases (expected = `None`) to `DATASET`.
