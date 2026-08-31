---
name: obsidian-notes
version: "1.0"
description: >
  Conventions and workflow for organizing notes in the personal Obsidian vault at ~/Documents/Obsidian.
  Use when creating, filing, renaming, or tagging notes; standardizing existing notes; or auditing
  tags/folders. Triggers: "obsidian", "my notes", "meeting notes", "file this note", "organize my notes",
  "standardize notes", "fix the tags", "namespace tags", "vault", "ARTI note", "note convention".
---

# Obsidian Notes Management

Standard for the personal Obsidian vault at `~/Documents/Obsidian`. The goal is a consistent,
low-friction structure: descriptive dated filenames, a small controlled tag vocabulary, and a
predictable file layout. Prefer editing/relocating existing notes over creating new ones.

## Vault layout

```
~/Documents/Obsidian/
  ARTI/       # all ARTI work notes (investigations, tickets, meetings, references)
  Writing/    # long-form / essay drafts
```

- Stay **flat inside a folder**. Filenames carry topic + date, so subfolders add friction without value.
- Every work note lives under `ARTI/`. Do not leave notes at the vault root.

## Filename convention

```
<Topic or Ticket> - <Descriptor> - <YYYY-MM-DD>.md
```

Examples:
- `INTEL-768 Webpage Eval Failure Analysis - 2026-08-27.md`
- `Arti External - Microsoft Infra Walkthrough - 2026-08-31.md`

Rules:
- Date suffix `- YYYY-MM-DD` is required on work notes.
- Use the real ticket ID as the prefix when the note is ticket-scoped.

## File structure (inside each note)

1. `# H1 Title` — plain title, no date, no tags.
2. A **single tag line** directly under the H1 (blank line between).
3. A lead section: `## Summary` or `## TL;DR` in prose, **bolding** the key findings.
4. Detail sections with descriptive headers; tables for structured data; `[[wikilinks]]` to related notes.
5. `## Action Items` as GitHub checkboxes (`- [ ]`) when the note produces follow-ups.

Separate **resolved facts** (plain bullets) from **open questions** (prefix `- **Q:**` or `- **Open:**`).

## Tag vocabulary (controlled)

Tags use `/` namespaces so they cluster in Obsidian's tag pane. One tag line per note, space-separated.

### Scope — where the work lives
- `#arti/external` — externally-facing ARTI work
- `#arti/internal` — internal ARTI work

Never use the old flat spellings `#arti-external`, `#external-arti`, `#internal-arti`. Normalize on sight.

### `#type/*` — the note type. Exactly ONE per note. Only these four:

| Type | Use when |
| --- | --- |
| `#type/ticket` | Work scoped to a Jira/tracked ticket (`INTEL-*`, etc.) |
| `#type/investigation` | Ad-hoc dig / debugging with **no** ticket scope |
| `#type/reference` | Durable "how this works" explainer, not a point-in-time dig |
| `#type/meeting` | Meeting / sync notes |

Decision rule: ticket-numbered work -> `#type/ticket`; ad-hoc dig -> `#type/investigation`;
lasting explainer -> `#type/reference`; meeting -> `#type/meeting`.

Do **not** reintroduce granular types like `analysis`, `audit`, `baseline`, `eval`, `follow-up`.
Their specificity already lives in the topic tags and the ticket tag.

### `#ticket/*` — ticket reference (independent of type)
- `#ticket/INTEL-768`, `#ticket/INTEL-798`, `#ticket/6419` (bare GitHub issue numbers get the `#ticket/` prefix too).
- A ticket-scoped note carries both `#type/ticket` and one or more `#ticket/<id>`.

### Topic tags — plain, no namespace
Free-form but reuse existing ones: `#webpages #taxonomy #ingestion #i18n #intellum #milk #algolia
#internal-api #data-lineage #security #azure-infra`.

### Relationship / status — plain, not a type
- `#follow-up` marks a note that follows up on another (pair with a `[[wikilink]]`). It is **not** a `#type/*`.

## Common workflows

### Filing a new note
1. Draft under `ARTI/` with a convention-compliant filename (topic/ticket + descriptor + date).
2. Add H1, then the tag line: scope + exactly one `#type/*` + any `#ticket/*` + topic tags.
3. Lead with a `## Summary`.

### Standardizing / auditing tags
1. Read the real tag line of each file (line under the H1). Inline `#refs` inside prose or tables
   (e.g. GitHub `#6419` in a sentence, or `#1`/`#2` list references) are **not** tags — do not touch them.
2. Fix scope collisions -> `#arti/external` / `#arti/internal`.
3. Ensure exactly one `#type/*` from the four-item set.
4. Namespace ticket references under `#ticket/*`.
5. Demote `follow-up` from `#type/*` to plain `#follow-up`.
6. Add a tag line to any untagged work note.

### Relocating a note into the vault
- Move to `ARTI/` and rename to the dated convention in the same step.

## Guardrails
- Never use the em dash. Use a plain dash.
- Do not create speculative notes or docs; edit existing ones.
- When distinguishing tags from inline references, always inspect the line context first — only the
  single line beneath the H1 (or top of file) is the tag line.
