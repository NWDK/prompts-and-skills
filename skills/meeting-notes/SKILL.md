---
name: meeting-notes
description: >
  Turn an AI-generated meeting transcript (e.g. a Gemini / Otter / Fireflies export) into structured, filed action items across your projects, plus a consolidated punch list. Use when someone drops a transcript export into an inbox folder or asks to "process the transcript", "triage the meeting notes", "extract action items from this call", "/meeting-notes <file>". Modal by meeting type via a variant file. Always proposes routing first and waits for confirmation before filing.
---

# Meeting Notes

Process a meeting transcript into:
1. A cleaned, glossary-corrected transcript
2. Action items extracted, clustered by project, with assignees
3. Decisions logged (aligned, shelved, needs-discussion)
4. Open questions surfaced
5. Per-project meeting-extract notes filed into each project's notes folder (after the user confirms routing)
6. (Optional) a refreshed coordination current-state snapshot
7. (Optional) a consolidated punch-list HTML, ready to publish

> **Customize before first use.** This skill is generic. The places that depend on your setup — your project list and aliases, your filing paths, your transcription tool's quirks (the "glossary"), and your publishing step — are marked with **`CUSTOMIZE`** blocks. Fill those in once and the pipeline runs.

## When to use

- Someone drops a transcript export into your transcript inbox folder
- "process the transcript", "triage the meeting notes", "/meeting-notes <path>", "extract action items from this meeting"
- A companion file (e.g. a `.docx`) sits alongside the transcript — that often signals embedded screenshots worth extracting

## When not to use

- A one-off action item mentioned in chat — just write it down
- A transcript from a tool whose artifact pattern you haven't taught the skill yet — build a new variant first
- A transcript already processed and filed (check the inbox for an `archive/<date>/` marker)

## Variants

A "variant" is a per-meeting-type config: the project routing table, filing destinations, and any output format specific to that meeting type (e.g. a team sync vs a customer call vs a dev standup). Keep each variant in `variants/<variant>.md`.

Pick the variant by:
1. Explicit argument (`/meeting-notes <variant> <path>`)
2. The intake subfolder the file sits in (e.g. `inbox/<variant>-transcripts/`)
3. Ask the user if neither is clear — do not guess.

```
CUSTOMIZE — Variants
List your meeting types and where each one's config lives. Example:
- team-sync   → variants/team-sync.md
- customer    → variants/customer.md
- dev-standup → variants/dev-standup.md
A variant file holds: the project routing table (aliases → canonical project →
filing destination), any current-state target, and the output format for that type.
A starter template is in variants/example.md.
```

## Pipeline (shared across variants)

### Step 1 — Pre-flight

Verify before doing anything. Halt and report which check failed; do not silently recover.

1. **File exists** and is readable.
2. **Looks like the expected transcript format** — most AI note-takers emit a recognisable structure (a summary block, a decisions block, a timestamped transcript). If the structure differs from what your variant expects, halt — it may be a different tool needing its own handling.
3. **Variant identified** (see above).
4. **Variant file readable** at `variants/<variant>.md`.
5. **If a companion document sits alongside** (e.g. a `.docx`): note it; screenshots get handled in Step 4. If none, skip screenshot handling.

### Step 2 — Cleanup

Many auto-transcribers have a known artifact: the active speaker's captions get duplicated onto the other speaker's track as a fragmented "echo". Strip it.

The pattern looks like:
```
**Speaker A:** This is the original phrase.

**Speaker B:** This is the
```
where Speaker B's line is a phantom echo of Speaker A's words, often truncated or trailing off mid-word.

Heuristic for detection:
- Same words appear in consecutive speaker blocks
- The second block is shorter, fragmented, or trails off mid-word
- Adjacent timestamps are within a few seconds

Strip the phantom echo. Keep only the genuine speaker's line. When uncertain, preserve both and flag inline with `[possible echo]` for the user to review.

Apply your glossary corrections (transcriber misspellings of names, products, vendors). Output the cleaned transcript to a working scratch location. Do not modify the original intake file.

```
CUSTOMIZE — Glossary
Maintain a glossary-corrections file of the misspellings your transcriber
routinely produces (people, products, tools, jargon). Apply it during cleanup.
A starter pattern is in glossary-corrections.md.
```

### Step 3 — Extraction

Three passes over the cleaned transcript.

**Pass A — Action items.** Look for:
- Direct assignments ("you'll come back to me on X", "I'll take Y")
- Implicit assignments (someone volunteers, or the other party accepts)
- Anything explicitly flagged as belonging on the shared list

The transcriber's own "next steps" / summary block is a starting point, never ground truth. Always re-scan the transcript body — automated passes routinely miss 20–50% of actual asks, and sometimes merge two distinct asks into one. Read the summary, decisions, AND details blocks first, then re-scan the body to fill gaps.

For each action item, capture: assignee, project (best guess), the ask in one line, a source quote (one short phrase + timestamp).

**Pass B — Decisions.** Aligned (agreed), shelved (ruled out), needs-discussion (unresolved). Use the transcriber's decisions block as a start, then re-scan.

**Pass C — Open questions.** "I don't know if…", "we should ask…", "still need to figure out…". These don't all become action items but should be surfaced.

### Step 4 — Screenshot extraction (only if a companion doc is present)

Convert the companion doc, extract embedded images to a working location. For each image: note where in the transcript it appeared; keep only genuinely useful context (a design review, a comparison); discard reactions, blank slides, decorative images. Useful images get filed alongside the relevant project's meeting-extract note. If no companion doc, skip this step.

### Step 5 — Routing proposal

Load the variant file. It contains the project list with aliases, filing destinations per project, and the punch-list format.

For each action item and decision, propose a route. For ambiguous items, flag rather than auto-route.

**Present the routing proposal to the user and STOP.** Do not file anything. Format:

```
ROUTING PROPOSAL — <variant> meeting, <date>

Project: <project-name>
  - [Action] <assignee>: <one-line ask>  (source: <quote> @ <timestamp>)
  - [Decision] <aligned/shelved/needs-discussion>: <statement>

AMBIGUOUS — needs your call:
  - <item>: route to <option A> or <option B>?

UNROUTED — couldn't match to a project:
  - <item>
```

Wait for the user to confirm, redirect, or amend.

### Step 6 — Filing (after approval)

For each project, write a meeting-extract note. Structure:
```markdown
# <Variant> Meeting Extract — YYYY-MM-DD

Source: <path to the intake transcript>
Attendees: <names>

## Action items
- **<assignee>** — <one-line ask>
  > <quote excerpt> [@<timestamp>]

## Decisions
- **Aligned**: <statement>
- **Shelved**: <statement>
- **Needs discussion**: <statement>

## Open questions
- <question>

## Screenshots (if any)
![<caption>](./screenshots/<file>.png)
```

For decisions that materially change a project's direction, also append a one-line entry to that project's status/decision log — do not rewrite the overview wholesale. If a project's notes folder doesn't exist, halt and ask the user where to file rather than creating folders unprompted.

```
CUSTOMIZE — Filing destinations
Define where extracts land per project, e.g.
<workspace>/projects/<project-slug>/notes/YYYY-MM-DD-<variant>-meeting-extract.md
Keep meeting extracts separate from your working session notes — different lifecycle.
```

### Step 7 — Coordination current-state (if the variant defines one)

Some variants maintain a "current state" snapshot separate from the per-meeting extracts — a quick "what do I owe / what am I waiting on" read. If the variant specifies a current-state target, overwrite it now with the new snapshot (a complete refresh, not an append). Skip if the variant doesn't define one.

### Step 8 — Punch-list generation

Generate the consolidated punch-list HTML per the variant's spec (one self-contained file, inline styles, no external assets). Save to a working location. Offer to publish — but do not auto-publish; that's the user's explicit call.

```
CUSTOMIZE — Publishing
If you publish the punch list to a live URL, name your publishing step here.
Otherwise leave the HTML at the working path for the user to open.
```

### Step 9 — Archive

Move the intake transcript (and companion doc) from the inbox to `inbox/<variant>-transcripts/archive/<date>/`. Keeps the inbox clean and prevents accidental reprocessing.

## Hard DON'Ts

- Do not file anything before the user has confirmed the routing proposal.
- Do not auto-publish — handing off the HTML is the user's call.
- Do not trust the transcriber's summary/next-steps as complete — always re-scan the body.
- Do not create new project folders. If routing suggests a project with no folder, surface it.
- Do not modify the original intake transcript — always work from a cleaned copy.
- Avoid time-based language in the outputs ("by Friday", "this week") if your team tracks by state rather than date — state-code instead (Active / In progress / Blocked / Needs input).
