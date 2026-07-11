---
name: feedback
version: "2.1"
description: >
  Find and triage all FEEDBACK: comments in a repo, evaluate each file's comments with a
  subagent, ask the user to decide on each item directly in the UI, then implement the chosen
  fixes with one subagent per file (no two agents touch the same file). Each addressed item is
  logged as an error-class label whose recurrence trend can be visualized on request. Triggers:
  "feedback comments", "review feedback", "check FEEDBACK", "triage feedback", "address feedback",
  "FEEDBACK:", "feedback labels", "visualize feedback labels", "error-class trends"
---

# Feedback: Triaging FEEDBACK: Comments

This skill finds every `FEEDBACK:` comment left in the codebase (typically by a reviewer,
teammate, or past-you) and turns each one into a short, decision-ready question for the user -
not a wall of raw comments, and not a silent auto-fix. Decisions are gathered directly in the UI
via the question tool; once every decision is made, the actual code changes are made by
subagents, one per file, so no two agents ever edit the same file at once.

Every addressed item is also logged as an **error-class label** so recurrences are counted over
time and their trend can be visualized on demand.

**Bundled resources** (in this skill's directory, resolve `<skill_dir>` via `/skills info
feedback`):
- `scripts/labels.py` - self-contained Python 3 (stdlib only) tool that tracks error-class labels
  and renders a time-series visualization. Subcommands: `view_labels`, `add_labels`,
  `visualize_labels`. It stores data by convention at `<repo-root>/.feedback/labels.json` and
  writes the visualization to `<repo-root>/.feedback/labels.html` (paths are fixed, no overrides).
  Run it as `python3 <skill_dir>/scripts/labels.py <subcommand> [opts]`.

## 1. Find every FEEDBACK: comment

Search the whole repo (not just the cwd) for the marker, case-sensitive, across all text/code
files. Prefer `rg` (ripgrep) when it's available on the system - it's faster and respects
`.gitignore`-style excludes automatically:

```bash
rg -n "FEEDBACK:" .
```

Fall back to plain `grep -rn "FEEDBACK:" .` only if `rg` isn't installed. The `grep` tool (which
is ripgrep-backed) is also a good option when available. Capture, for each match: file path and
line number.

If zero matches are found, report that immediately and stop - don't invent work.

## 2. Dispatch one subagent per file to triage

Group the matches from step 1 by file - a single file may contain multiple `FEEDBACK:` comments,
and one subagent should handle all of them together (it only needs to read the file once, and
can spot relationships between nearby items). Launch one `general-purpose` or `explore` subagent
per distinct file (background mode, in parallel - launch all of them in the same turn since
files are independent of each other). Don't over-constrain the subagent or hand it pre-extracted
context - just point it at the file and the line numbers and let it look around on its own. Give
it a prompt along the lines of:

- The file path and the full list of line numbers where `FEEDBACK:` comments live in this file -
  go read the file (and whatever surrounding code/context it needs) directly.
- For each comment in the file, independently: explain *what* the feedback is asking for and
  *why* it likely matters, concisely.
- For each comment, if there are multiple reasonable ways to address it, propose 2-3 concrete
  options with a one-line tradeoff each. If there's really only one sane fix, say so instead of
  manufacturing false choices.
- For each comment, provide a one-line sentence naming the general *error class* or feedback
  category it belongs to (e.g. "missing input validation on user-facing forms", "inconsistent
  error handling in async code", "N+1 query pattern") - phrased generically enough that it could
  apply to other, similar occurrences elsewhere in the codebase, not just this one instance.
- Do not modify any code - this is an evaluation/triage pass only, not an implementation pass.
- Do not look at or reference CLAUDE.md - that comparison is the main agent's job, not the
  subagent's.
- Return a short structured result as a list, one entry per feedback comment in the file: `file`,
  `line`, `summary`, `error_class` (the one-line sentence), `options` (list of `{label,
  tradeoff}`, may be empty or single-item if not applicable).

Do not have subagents fix the code in this pass - the user reviews options first, then decides
what (if anything) to implement in the follow-up step.

## 3. Consolidate the triage results

Once all subagents complete, flatten every file-subagent's list into a single ordered list of
feedback items (sorted by file, then line). Keep it in memory or in the session database (the
`todos` table works well: one row per item, `id` = file+line, `description` = summary + options).
Each item should carry: `file`, `line`, `summary`, `error_class`, `options`, and empty slots for
the user's `decision` and any free-form `notes`. This is just your working ledger - there is no
report server and no JSON schema to satisfy anymore.

## 4. Ask the user to decide on each item, in the UI

Walk through the consolidated items and gather a decision for each one using the question tool
(the `ask_user` tool) so each choice is presented as a proper UI prompt - never dump the whole
list as plain text and never guess silently.

- Ask about **one item at a time**. For each item, give a short one-line restatement of the
  feedback, then present the subagent's proposed options as the choices.
- When an item has multiple options, pass them as the `choices` array (add a "Skip / don't
  address" choice implicitly - the tool already offers a freeform box, so the user can also type
  a custom instruction). If you have a recommended option, put it first and mark it
  "(Recommended)".
- When an item has only one sane fix, still ask - offer "Apply the fix" vs "Skip" so the user
  stays in control.
- Record each answer (the chosen option label plus any freeform note the user typed) back onto
  that item as its `decision` / `notes` before moving to the next question.
- Keep questions tight and decision-focused; don't re-explain the whole codebase. If several
  items are truly trivial and closely related, it's fine to confirm them together in a single
  question, but default to one question per item.

After all items have a decision, briefly summarize back to the user which items will be
implemented (and with which option) and which will be skipped, so they can course-correct before
any code changes.

## 5. Implement the chosen fixes with one subagent per file

Group the items the user chose to address by **file**. Then launch `general-purpose` subagents to
make the changes - **exactly one subagent per file**, so that no two agents ever modify the same
file concurrently. Files are independent, so launch these in parallel (all in the same turn,
background mode). This is the core of the simplified design: parallel where safe, serialized
per-file where a conflict would otherwise occur.

Give each per-file implementation subagent a prompt containing:

- The file path it owns, and the full list of feedback items for that file, each with: the line
  number, the summary, the user's chosen option (the `decision`), and any freeform `notes` the
  user added. Instruct it to implement **only** those decisions.
- Instruction to make precise, surgical edits that fully address each chosen item, following the
  user's selected option (and honoring their notes), and to remove or update the corresponding
  `FEEDBACK:` comment once the item is resolved.
- A hard boundary: it may edit **only** the one file it was assigned. If a change appears to
  require touching another file, it must stop and report that back rather than editing outside
  its lane - cross-file coordination is the main agent's job, not the subagent's.
- Instruction to skip any item the user chose not to address, and to leave that `FEEDBACK:`
  comment in place.
- Do not touch CLAUDE.md.

If two feedback items genuinely require a coordinated change spanning multiple files, handle that
coordination yourself (main agent) rather than giving overlapping files to parallel subagents.

Once all per-file subagents finish, run the project's existing lint/tests if present to confirm
nothing broke, and summarize what changed.

## 6. Record an error-class label for each addressed item

For every feedback item that was **actually addressed** in this round (skip anything the user
declined), log it against an error-class label so recurrences accumulate over time. Do this with
the bundled `scripts/labels.py` - the main agent owns the semantic matching; the script itself is
deliberately dumb about meaning.

1. Load the existing labels once: `python3 <skill_dir>/scripts/labels.py view_labels --json`.
2. For each addressed item, semantically compare its `error_class` sentence to the existing labels:
   - **Matches an existing label** -> increment it by its slug:
     `... add_labels --slug <slug> --file <path> --line <n>`
   - **Genuinely new error class** -> create it with a short handle and the fuller sentence:
     `... add_labels --name "<short-handle>" --description "<error_class sentence>" --file <path> --line <n>`
   - Keep the short `name` compact (e.g. `input-validation`, `n-plus-one`); put the readable
     explanation in `--description`.
3. The script auto-captures the current git branch and latest commit hash for each occurrence, and
   defaults the timestamp to now - you don't pass those.

You can add several occurrences in one invocation via `--items <path.json>` (a JSON array of
`{name+description | slug, file, line}` objects) if you prefer a single batched call. Only
addressed items ever create or increment labels - this mirrors the CLAUDE.md rule that an error
class isn't codified until the underlying issue is actually fixed.

## 7. Loop until the user confirms they're fully done

Feedback triage may take multiple rounds - the user might only act on some items now, add new
`FEEDBACK:` comments, or want another pass after seeing the implemented changes. Once the per-file
implementation subagents from step 5 have finished (and their labels recorded in step 6), the main
agent must ask the user - using the question tool (`ask_user`) so it shows as a UI prompt - what to
do next. Present it as a choice between roughly these options:

- **More feedback** - there are new/remaining `FEEDBACK:` comments to handle, or they want another
  pass. If chosen, go back to step 1 (or step 4 if items already exist and just need re-decision)
  rather than proceeding.
- **Discuss CLAUDE.md changes** - they're done implementing and want to move on to reconciling the
  addressed error classes against CLAUDE.md. If chosen, proceed to step 8.
- **Done** - nothing further; stop here without touching CLAUDE.md.

Do not move on to step 8 (or stop) until the user explicitly picks one of these. Don't infer
completion from silence or from a single round alone - ask directly.

## 8. Reconcile error classes against CLAUDE.md - only after the user confirms they're done, and only for feedback that was actually addressed (main agent only, not subagents)

Only run this step once the user has confirmed in step 7 that all rounds of feedback are
complete, and only for feedback items that were actually implemented across those rounds. Skip
it entirely for any items the user chose not to act on - an error class shouldn't be codified
into CLAUDE.md until the underlying issue has actually been fixed. Subagents never touch
CLAUDE.md - this cross-item comparison and any editing decisions are the main agent's
responsibility alone.

- Look for a `CLAUDE.md` at the repo root (check likely nearby locations too if not found at
  root). Read it if present.
- If it has a `## Guidelines` section (or similarly named, e.g. "Guidelines", "Conventions"),
  compare each addressed item's `error_class` sentence against the existing bullets:
  - If an existing bullet already covers the same error class, note the match to the user and
    don't duplicate the bullet.
  - If it's a genuinely new error class, propose adding it as a new bullet point.
- A label with a high recurrence count (visible via `view_labels`) is a strong signal the error
  class belongs in the Guidelines - mention that when proposing bullets.
- If `CLAUDE.md` exists but has no `Guidelines` section, propose creating one and seeding it with
  the new error-class bullets.
- If `CLAUDE.md` doesn't exist at all, mention that too and ask whether the user wants one
  created, rather than assuming.
- Present the proposed diff/bullets to the user. Do not write to `CLAUDE.md` until the user
  explicitly accepts the change.

## Visualizing label trends (user-triggered only)

`visualize_labels` renders `<repo-root>/.feedback/labels.html` - a self-contained offline page
(no internet needed) plotting each label's cumulative occurrences over time, with per-label
show/hide checkboxes, optional trend lines, and a day/week granularity toggle. Hovering a point
surfaces the label description plus that occurrence's file, branch, and commit.

Run it **only when the user explicitly asks** to see label trends (e.g. "visualize the feedback
labels", "show me the error-class trends"). The agent must never auto-run it at the end of a pass
or offer it as part of the loop in step 7. When asked:

```bash
python3 <skill_dir>/scripts/labels.py visualize_labels
```

Then tell the user the written path (add `--open` to open it in the default browser on macOS).
This skill can also be triggered purely to `view_labels` or `visualize_labels` without running a
full feedback pass.
