---
name: note-taking
version: "1.0"
description: >
  Methodology and conventions for organizing personal notes (Markdown / Obsidian-style vaults):
  descriptive dated filenames, a controlled namespaced tag vocabulary, and consistent file structure.
  Use when creating, filing, renaming, or tagging notes; standardizing existing notes; auditing tags;
  or deciding on a tag scheme. Triggers: "my notes", "meeting notes", "file this note", "organize my
  notes", "standardize notes", "fix the tags", "namespace tags", "note convention", "note-taking".
---

# Note-Taking

A portable methodology for keeping a Markdown note vault consistent: descriptive dated filenames, a
small controlled tag vocabulary, and a predictable per-note structure. The **method** is fixed; the
**specific vocabulary** (which scope tags, which note types, which ticket prefixes, which topics) is
per-vault and lives in a config file, not in this skill. Prefer editing/relocating existing notes over
creating new ones.

## Step 0 — Load the vault's conventions

Before creating, filing, or auditing notes, locate the vault's convention config:

- File name: `.notes-conventions.json`, found by walking **up** from the note being edited to the
  vault root (the nearest directory containing `.obsidian/`, or the top of the notes tree).
- Read it. It defines the concrete vocabulary this vault uses: `filenamePattern`, `scopeTags`,
  `types`, `ticketPrefixes`, `topicTags`, and `folders`.

If no config exists, **do not guess a scheme.** Ask the user to decide the vocabulary (see
"Establishing conventions" below), then write `.notes-conventions.json` so it is reused next time.
When the user introduces a new tag/type/topic mid-task, update the config file in the same edit.

The config is the source of truth for *what* the tags are. This skill is the source of truth for
*how* they are structured and applied.

## Filename convention

Follow the vault's `filenamePattern`. The default pattern is:

```
<Topic or Ticket> - <Descriptor> - <YYYY-MM-DD>.md
```

- A trailing `- YYYY-MM-DD` date is required on work notes.
- Use the real ticket/topic ID as the prefix when the note is ticket-scoped.

## File structure (inside each note)

1. `# H1 Title` - plain title, no date, no tags.
2. A **single tag line** directly under the H1 (blank line between).
3. A lead section: `## Summary` or `## TL;DR` in prose, **bolding** the key findings.
4. Detail sections with descriptive headers; tables for structured data; `[[wikilinks]]` to related notes.
5. `## Action Items` as GitHub checkboxes (`- [ ]`) when the note produces follow-ups.

Separate **resolved facts** (plain bullets) from **open questions** (prefix `- **Q:**` or `- **Open:**`).

## Tag system (structure is fixed; values come from config)

One tag line per note, space-separated. Tags use `/` namespaces so they cluster in the tag pane.
Four categories, applied in this order:

1. **Scope** - where/whose work it is. Values from `scopeTags` (e.g. `#area/external`). Namespaced.
2. **Type** - the kind of note. Exactly **ONE** per note, drawn from the `types` set in config.
   Keep this set small (typically 3-5). Do not invent granular one-off types; specificity belongs in
   topic and ticket tags.
3. **Ticket** - references to tracked work, namespaced under `#ticket/*` (e.g. `#ticket/INTEL-768`).
   Bare issue numbers still get the `#ticket/` prefix. Independent of type; a ticket note usually
   carries both a `#type/...` and one or more `#ticket/...`.
4. **Topic** - plain, un-namespaced subject tags, reused from `topicTags` in config.

Relationship/status markers (e.g. `#follow-up`) are plain tags, **not** a `#type/*`.

Normalize on sight: collapse flat spelling collisions into the namespaced form defined in config
(e.g. `#foo-external` / `#external-foo` -> the single `scopeTags` value).

## Common workflows

### Filing a new note
1. Load `.notes-conventions.json` (Step 0).
2. Create the file in the correct folder with a convention-compliant, dated filename.
3. Add H1, then the tag line: scope + exactly one type + any ticket tags + topic tags.
4. Lead with a `## Summary`.

### Standardizing / auditing tags
1. Load the config so you know the target vocabulary.
2. Read the **real tag line** of each file (the single line beneath the H1). Inline `#refs` inside
   prose or tables (e.g. a GitHub `#6419` in a sentence, or `#1`/`#2` list references) are **not**
   tags - never touch them.
3. Fix scope collisions to the namespaced `scopeTags` value.
4. Ensure exactly one `#type/*` from the config's `types` set.
5. Namespace ticket references under `#ticket/*`.
6. Demote any relationship marker (e.g. `follow-up`) out of `#type/*` to a plain tag.
7. Add a tag line to any untagged work note.

### Establishing / changing conventions (with the user)
When there is no config, or the user wants to change the scheme:
1. Propose a concrete vocabulary grounded in the notes that already exist (survey current tags first).
2. Keep the `types` set small; push back on over-splitting.
3. Get the user's decision, then write/update `.notes-conventions.json`.
4. Optionally offer to re-standardize existing notes to the agreed scheme.

## `.notes-conventions.json` shape

```json
{
  "filenamePattern": "<Topic or Ticket> - <Descriptor> - <YYYY-MM-DD>.md",
  "folders": { "Work": "day-to-day work notes", "Writing": "long-form drafts" },
  "scopeTags": ["#area/external", "#area/internal"],
  "types": {
    "ticket": "work scoped to a tracked ticket",
    "investigation": "ad-hoc dig with no ticket scope",
    "reference": "durable how-it-works explainer",
    "meeting": "meeting / sync notes"
  },
  "ticketPrefixes": ["INTEL-", "PROJ-"],
  "topicTags": ["#topic-a", "#topic-b"],
  "statusTags": ["#follow-up"]
}
```

## Guardrails
- Never use the em dash. Use a plain dash.
- Do not create speculative notes or docs; edit existing ones.
- Do not hardcode vault-specific values (folder names, scope tags, topics) into decisions - read them
  from the config so the skill stays portable across vaults.
- When distinguishing tags from inline references, inspect line context: only the single line beneath
  the H1 (or top of file) is the tag line.
