# Variant — Example (team sync)

A variant config for one meeting type. Copy this to `variants/<your-variant>.md` and fill it in. This example models a recurring internal team sync that spans several projects.

## Trigger conditions

This variant applies when any of these is true:
- The transcript sits in `inbox/team-sync-transcripts/<date>/`
- The user invokes `/meeting-notes team-sync <path>` explicitly
- The transcript's attendee list matches this meeting's regular participants

If a transcript has other attendees (a customer, a contractor, an exec), it's probably a different meeting type — halt and tell the user a different variant is needed.

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
- **Carry-over items** — when generating, scan the most recent extract in each project's notes folder for items not marked done; include them at the top of that project's section, annotated `(carried from YYYY-MM-DD)`.

## Hand-off to publishing (optional)

After the HTML is generated: show the user (a local file link is fine), ask whether to publish, and only publish on an explicit yes. Never auto-publish.
