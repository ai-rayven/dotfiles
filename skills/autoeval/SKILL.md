---
name: autoeval
version: "1.0"
description: >
  Iterative prompt-evaluation workflow using promptfoo. Triggers: "promptfoo", "run the eval", "prompt eval", "judge alignment", "fix eval failures",
  "iterate on the prompt", "improve pass rate", "eval loop"
---

# Autoeval: Iterative Prompt Evaluation with promptfoo

This skill defines the standard loop for evaluating and improving a prompt (especially an
LLM-as-judge prompt) against a ground-truth/annotated dataset using `promptfoo`. The goal is
not a specific prompt or dataset - it's the **process**: verify wiring cheaply, run the full
eval, analyze failures quantitatively, fix the single highest-leverage issue, and repeat.

"Good performance" is whatever the user defines (a target pass rate, zero regressions vs. a
prior run, etc.) - this skill does not decide that threshold. It owns the mechanics of getting
there efficiently.

## 0. Prerequisites for any promptfoo eval in this workflow

- Test cases MUST be authored/generated as a `tests.json` file (an array of promptfoo test
  case objects - `description`, `vars`, `assert`, `metadata`), not inline YAML lists in
  `promptfooconfig.yaml`. This keeps large or generated datasets (e.g. exploded from an
  annotated ground-truth JSON file) easy to regenerate, diff, and load with a script, and keeps
  `promptfooconfig.yaml` small and stable.
- If the dataset comes from an existing annotated JSON file (human labels, ground truth, etc.),
  write a small conversion script that explodes it into `tests.json` matching promptfoo format - one test case per
  labeled example - skipping any rows that aren't actually labeled yet. This will become the file used in promptfoo.
- Each test case's `assert` should compare the provider's output against the ground-truth label
  carried in that test's own `vars`/`metadata`, so pass rate == agreement rate with ground truth.

## 1. Verify wiring cheaply before a full run

Never launch a full eval as the first run after a config/provider change. Use
`--filter-first-n` (or `-n`) to run only the first N test cases first:

```bash
promptfoo eval -c promptfooconfig.yaml --filter-first-n 1 --no-cache -o /tmp/smoke.json
```

Confirm:
- The provider actually invoked (no import/auth/env errors).
- The prompt rendered correctly (vars substituted, no leftover `{{ }}` or template syntax
  errors - watch especially for literal JSON braces in the prompt colliding with Nunjucks
  `{{ }}` syntax; wrap literal braces in `{% raw %}...{% endraw %}`).
- The output shape matches what the assertion expects (e.g. valid JSON with a `result` field).

Only proceed to the full run once the smoke test passes with 0 errors.

## 2. Run the full eval, always with JSON output

Always pass `-o <path>.json` (or `--output`) so results are machine-readable - never rely on
the terminal table alone for analysis:

```bash
promptfoo eval -c promptfooconfig.yaml --no-cache -o /tmp/eval_result.json
```

Use `--no-cache` while iterating on the prompt (otherwise you'll silently get stale cached
judge responses for unchanged inputs and think a prompt fix had no effect).

## 3. Analyze the JSON output to find failures

Parse `/tmp/eval_result.json` (structure: `results.results[]`, each with `success`, `vars`,
`response`/`output`, `gradingResult` or per-assert `componentResults`). Filter to failing rows:

```python
import json
data = json.load(open("/tmp/eval_result.json"))
rows = data["results"]["results"]
failures = [r for r in rows if not r["success"]]
print(f"{len(failures)}/{len(rows)} failed")
```

For each failure, pull the test's `description`/`metadata` (expected label), the actual
`output`/judge verdict, and the judge's rationale (if present in the output). Print or save a
compact table of failures for triage - don't eyeball the raw JSON.

## 4. Tally failures to find the highest-priority fix

Don't fix the first failure you see - group failures by a shared root cause and fix the pattern
with the largest count first (highest leverage per prompt edit):

- Group by expected label (e.g. are failures skewed "should be yes, judge said no" vs. the
  reverse? - that points at a systematic bias, like a missing rule or overly strict wording).
- Group by a semantic category if one exists in the data/metadata (e.g. question type, source
  language, truncation, "distinct categories" vs. "enumerated identifiers" - whatever
  dimensions the underlying prompt already encodes as decision rules).
- Read the judge's own rationale text across failures for repeated phrases/reasoning patterns -
  that's usually the fastest way to spot "the judge is applying rule X when it shouldn't" or
  "the prompt has no rule covering scenario Y".
- Pick the single largest cluster. Resist the urge to fix multiple unrelated issues in one pass
  - you want a clean before/after comparison of pass rate per change.

## 5. Fix the prompt, not the test data

Edit the underlying prompt (and its single source of truth if the promptfoo `prompt.txt` is
generated from a Python/other constant - regenerate, don't hand-edit the generated file).
Typical fixes: add/clarify a decision rule, add an example, tighten ambiguous wording, fix a
formatting instruction the model is misreading. Do not change ground-truth labels to make the
judge "pass" - the annotations are the target, not a variable.

## 6. Re-run and compare

Re-run the full eval (`--no-cache`, `-o` a **new** path, e.g. include a timestamp or version
suffix) and diff pass rate and the specific failure cluster you targeted:

```bash
promptfoo eval -c promptfooconfig.yaml --no-cache -o /tmp/eval_result_v2.json
```

Confirm the targeted cluster improved and check you didn't regress previously-passing cases
(diff the two result JSONs' failing-test-id sets, not just the aggregate pass rate).

## 7. Loop

Repeat steps 3–6: re-analyze failures on the latest run, tally, fix the next-highest cluster,
re-run. Stop when the user's definition of "good enough" is met, or when further prompt edits
stop moving the needle (diminishing returns / conflicting failure clusters) - surface that
tradeoff to the user rather than silently continuing to churn.

