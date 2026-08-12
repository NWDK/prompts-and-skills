# Variant — Example (team sync / standup)

A variant config for one meeting type. Copy this to `variants/<your-variant>.md` and fill it in. This example models a recurring team standup that spans several projects.

**A variant is not just a routing table.** Roughly half of what makes extraction good lives below the routing section — how this meeting type actually sounds, which utterances are status rather than asks, who owns what when nobody is named. A variant that stops at the routing table produces thin extracts. Budget accordingly: a real one runs to a couple of hundred lines.

## Trigger conditions

This variant applies when any of these is true:
- The transcript sits in `inbox/team-sync-transcripts/<date>/`
- The user invokes `/meeting-notes team-sync <path>` explicitly
- The transcript's attendee list matches this meeting's regular participants

If a transcript has other attendees (a customer, a contractor, an exec), it's probably a different meeting type — halt and tell the user a different variant is needed.

## Speaker identification

Transcribers identify people inconsistently — by email in the header, by display name in the body, sometimes by a name that differs between the two. Map them once here so extraction doesn't have to guess. This extends `glossary-corrections.md`; the glossary fixes spellings, this table resolves *identity*.

| Appears as | Canonical person |
|---|---|
| `first.last@example.com` | First — their work email |
| `personal-handle@mailprovider.com` | First — their personal account; same person, different meeting invites |
| Display name with surname ("First Last") | First — use first name only in extracts |
| A role word the team uses out loud ("the designer", "our backend guy") | First — resolve to the person |

Record how you want them rendered in extracts (first name only is usually right) and note any identity you are guessing at, so the first run can confirm it rather than silently locking in an error.

## Project list and aliases

When routing action items, match transcript references to the canonical project using this table. Aliases are the terms people actually use out loud.

| Canonical project | Aliases (any of these route here) | Filing destination |
|---|---|---|
| `design-system` | "DS", "the design system", "components", "tokens" | `projects/design-system/notes/YYYY-MM-DD-team-sync-meeting-extract.md` |
| `marketing-site` | "the site", "website", "landing pages", "SEO" | `projects/marketing-site/notes/YYYY-MM-DD-team-sync-meeting-extract.md` |
| `mobile-app` | "the app", "iOS", "Android", "mobile" | `projects/mobile-app/notes/YYYY-MM-DD-team-sync-meeting-extract.md` |
| `coordination` | admin items, "I'll send you X", tooling that supports the team's own workflow | `projects/coordination/notes/...` — AND updates `projects/coordination/current-state.md` (see below) |

### Routing heuristics
- A feature-specific item routes to the project that owns that feature; if unclear, route to your "source of truth" project and flag.
- Prompt/AI-tooling items route to whichever project the prompt belongs to.
- Research/competitor items route to your strategy project unless clearly tactical for one project.
- Workflow / "I'll send you X" / housekeeping items route to `coordination`.
- An item you can't cleanly match goes in the AMBIGUOUS section — do not guess.

### Project has no folder yet
If routing identifies a project with no folder, surface it separately. Don't create folders — ask the user where to file.

## Extraction rules for this meeting type

The shared three-pass extraction in `SKILL.md` is the baseline. These are the adjustments a standup needs.

### Status updates are not action items

Standups are mostly status reporting. Extracting all of it as tasks produces a punch list nobody can use.

- **"I'm working on X"** → status: X in progress for `<speaker>`
- **"I finished Y" / "Y is done"** → status: Y closed by `<speaker>`
- **"I'm blocked on Z" / "waiting on Z"** → status: blocked, with the blocker named
- **"I'll pick up W next"** → upcoming work, not a hard commitment unless someone else accepts or confirms it

These go in a `## Status updates` section, separate from `## Action items`. Don't conflate the two.

### Assignee resolution

- Named directly ("Can you take X?") → that person.
- Volunteered ("I'll do X") → the speaker.
- Unowned ("we should fix...", "it needs to...") → fall back to project ownership, and say in the extract that ownership was inferred rather than stated.

Record your ownership defaults here — one line per project — so the unowned case has somewhere to land.

### Decisions are not tasks

A choice about *how* something will work is a decision, even when it sounds concrete and actionable. "We'll store it as a flat array rather than nested" belongs in `## Decisions`, not `## Action items`. Resist the pull to file it as a task because it is specific.

### Open questions that block

In a standup, an open question is often blocking someone's work. Flag any question where someone is currently waiting on the answer — those carry a different priority from curiosity-driven ones, and they're what the next meeting should open with.

## Meeting-shape patterns to recognise

These are the ones that mislead a naive extraction pass on this meeting type. Yours will differ — collect them as you notice them, because this section is what makes the variant earn its length.

- **Round-robin opener.** "Anyone want to go first?" / "I can start" signals structured per-person reporting. Treat each following speaker block as that person's status segment until the next handoff.
- **Demo narration is not an ask.** When someone shares a screen and narrates what they built, that is status. Distinguish walkthrough sentences from forward-looking commitments.
- **The closing ritual.** Most standups end with some version of "so what's blocking the release?" Capture the resulting plan as **one** decision about sequencing, not as N separate action items.
- **Deferred deep-dives are real items.** "Let's book a session on X" is an action item even though it's only scheduling. Capture it.
- **Dual classification is fine.** In-flight work often has a status face ("X is happening") and an action face ("next, do Y to it"). File both.
- **Re-check the transcriber's own "next steps" for state.** Those blocks don't distinguish already-done from in-progress from fresh ask. For each one, scan the body to find the actual state, then route to status or action accordingly.
- **Silence is not a gap to fill.** In a larger standup one attendee may have no status content at all. An empty section for them is correct — don't manufacture one.

## Output shape

### Per-project meeting-extract note

Same base structure as `SKILL.md` Step 6, plus the status section this meeting type needs:

```markdown
# Team Sync Meeting Extract — YYYY-MM-DD

Source: <path to the intake transcript>
Meeting type: Standup / Kickoff / Project sync
Attendees: <names>

## Status updates
- **<person>** — <one-line summary> · State: In progress / Closed / Blocked
  > <quote excerpt> [@<timestamp>]

## Action items
- **<assignee>** — <one-line ask>
  > <quote excerpt> [@<timestamp>]

## Decisions
- **Aligned**: <statement>
- **Shelved**: <statement>
- **Needs discussion**: <statement>

## Open questions
- <question> — _(blocking <who>, if applicable)_

## Screenshots (if any)
<one image link per kept screenshot>
```

### What this variant does not update

State the negative scope explicitly, or a future run will helpfully update something it shouldn't. For example: a coordination snapshot that tracks a specific two-person relationship should not be rewritten from a whole-team standup.

## Current-state update (optional)

If this variant maintains a quick "what do I owe / what am I waiting on" snapshot, overwrite it after filing. It's a snapshot, not a history — fully replace each run. State-coded, not time-coded.

```markdown
# <Team> — Current State
**Last updated**: YYYY-MM-DD

## What I owe
- **[<project>]** <one-line ask> · State: <Active/In progress/Blocked/Needs input>

## What I'm waiting on
- **[<project>]** <one-line ask> · State: <state>

## In flight
- **[<project>]** <one-line description>

## Recently closed
- **[<project>]** <one-line summary> · _closed YYYY-MM-DD_
```

## Punch-list HTML template

Self-contained, inline styles, no external assets. Neutral styling — swap colours/fonts for your own brand.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Punch List — YYYY-MM-DD</title>
<meta name="description" content="Active action items from the YYYY-MM-DD sync, grouped by project.">
<style>
  :root { --bg:#faf8f5; --ink:#1c1917; --muted:#78716c; --rule:#e7e5e4; --a:#2563eb; --b:#16a34a; --warn:#dc2626; }
  body { font-family: system-ui,-apple-system,"Segoe UI",sans-serif; background:var(--bg); color:var(--ink); max-width:820px; margin:2rem auto; padding:0 1.5rem; line-height:1.5; }
  h1 { font-size:1.6rem; margin-bottom:.25rem; } h1 + p { color:var(--muted); margin-top:0; }
  h2 { font-size:1.1rem; margin-top:2rem; border-bottom:1px solid var(--rule); padding-bottom:.25rem; }
  table { width:100%; border-collapse:collapse; margin-top:.75rem; }
  th,td { text-align:left; padding:.5rem .75rem; border-bottom:1px solid var(--rule); vertical-align:top; font-size:.92rem; }
  th { font-weight:600; color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; }
  .owner-a { color:var(--a); font-weight:600; } .owner-b { color:var(--b); font-weight:600; }
  .status { font-size:.78rem; color:var(--muted); }
  .ambiguous h2 { color:var(--warn); }
  footer { margin-top:3rem; color:var(--muted); font-size:.8rem; border-top:1px solid var(--rule); padding-top:1rem; }
</style>
</head>
<body>
<h1>Punch List</h1>
<p>From sync on YYYY-MM-DD. Active items only.</p>

<!-- Repeat one <h2> + <table> per project that has items -->
<h2>Project Name</h2>
<table>
  <thead><tr><th>Owner</th><th>Ask</th><th>State</th></tr></thead>
  <tbody>
    <tr><td class="owner-a">Person A</td><td>One-line ask. <span class="status">(source: short quote @timestamp)</span></td><td>Active</td></tr>
    <tr><td class="owner-b">Person B</td><td>One-line ask.</td><td>In progress</td></tr>
  </tbody>
</table>

<div class="ambiguous">
<h2>Needs routing</h2>
<table>
  <thead><tr><th>Owner</th><th>Ask</th><th>Possible homes</th></tr></thead>
  <tbody><tr><td class="owner-a">Person A</td><td>Ambiguous ask</td><td>Project A · Project B</td></tr></tbody>
</table>
</div>

<footer>Generated from the meeting transcript via the meeting-notes skill. State-coded, not time-coded.</footer>
</body>
</html>
```

Template notes:
- **Owner colour coding** — give each regular participant a colour; carry the same colours to carried-over items.
- **Carry-over items** — when generating, scan the most recent extract in each project's notes folder for items not marked done; include them at the top of that project's section, annotated `(carried from YYYY-MM-DD)`. Note that nothing in the pipeline marks items done — if you want carry-over to converge rather than grow, that has to become a habit or a step you add.

## Hand-off

After filing, report back:
- N action items filed across M projects
- Any flagged blockers (open questions where someone is waiting)
- Any items routed to topics with no folder yet, needing a filing decision
- **Any items that belong to a different meeting type.** Work surfaced in one meeting often needs a decision that happens in another. Those get orphaned if nobody flags them at hand-off, because this variant doesn't write to the other one's destinations.

## Publishing hand-off (optional)

After the HTML is generated: show the user (a local file link is fine), ask whether to publish, and only publish on an explicit yes. Never auto-publish.

## Provenance

Note when the variant was built, which meeting types it covers, and what it deliberately doesn't handle yet. A variant accumulates hard-won pattern knowledge — recording where it came from stops a future edit from undoing a lesson.
