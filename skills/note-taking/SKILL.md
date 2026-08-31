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

## Folder structure and the Inbox workflow

Folders and tags can each answer "where does this live" and "what is this." A vault picks, in config,
which axis drives its folders. The one hard rule: **whatever a folder encodes, it must stay in sync
with the tag that encodes the same thing** - pick a single source of truth per fact, or mirror them
deterministically. Never let folder and tag disagree.

Every vault has these lifecycle locations, named in config:

- `inbox` - the capture zone. **Every new note lands here first.** Nothing stays here long-term.
- `activeRoot` - the root for triaged, active notes.
- `archive` - done or inactive notes.

### Type-folder mirroring (when `typeFolders` is set in config)
Some vaults organize the file tree by note type for visual clarity, while still keeping the `#type/*`
tag for cross-folder aggregation (Dataview/search). When config defines `typeFolders` (a map from
each type to a folder), the folder and the tag are **kept in lockstep**:

- A note tagged `#type/ticket` lives in `typeFolders.ticket`, and vice versa.
- On triage/audit, the destination folder is derived from the note's `#type/*` tag. If a note's folder
  and tag disagree, the tag is authoritative - move the file to match, or fix the tag if it's wrong.
- Changing a note's type means moving the file **and** updating the tag together.

Non-type folders in `folders` are stable projects/areas or lifecycle stages. Introduce a **new** folder
only when a note genuinely does not fit an existing one - propose it to the user, then add it to config.

### Triage workflow
Run when asked ("triage my inbox") or opportunistically after capture. For each note in `inbox`:
1. Ensure it is convention-compliant (filename dated, H1, one tag line: scope + one type + tickets + topics).
2. Determine destination:
   - If `typeFolders` is configured, move to the folder for the note's `#type/*` tag.
   - Otherwise, move to the matching project/area folder.
   - New project/area needed -> propose the folder to the user, create it, add to config, move.
   - Done/ephemeral -> move to `archive` (or delete if truly disposable).
3. Never leave a triaged note in the inbox.

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

### Filing a new note (capture)
1. Load `.notes-conventions.json` (Step 0).
2. Create the file in the `inbox` folder with a convention-compliant, dated filename.
3. Add H1, then the tag line: scope + exactly one type + any ticket tags + topic tags.
4. Lead with a `## Summary`.
5. Triage now or later (see Triage workflow) to move it out of the inbox.

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
8. If `typeFolders` is configured, verify each note sits in the folder matching its `#type/*` tag;
   move any mismatches so folder and tag agree.

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
  "inbox": "Work/Inbox",
  "archive": "Work/Archive",
  "activeRoot": "Work",
  "folders": {
    "Work/Inbox": "capture zone - new notes land here first",
    "Work/Archive": "done / inactive notes",
    "Writing": "long-form drafts"
  },
  "typeFolders": {
    "ticket": "Work/Tickets",
    "investigation": "Work/Investigations",
    "reference": "Work/Reference",
    "meeting": "Work/Meetings"
  },
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
