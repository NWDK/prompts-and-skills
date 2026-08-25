# Templates

Text you paste somewhere and edit. No install, no tooling, no agent required.

A template lives here rather than in `skills/` because it is not instructions
for an agent to follow when it picks up a task. It is something you put in
place once, usually into a settings field, and then mostly forget about.

## What a template in here is, and is not

**Is:** a block of text with a job, sized and worded so it survives being
pasted into a box you do not control, plus the reasoning for every line in
it.

**Is not:** a skill. Skills are loaded per task and tell an agent how to work.
Templates are standing text. If a thing only makes sense when a particular
kind of work starts, it is a skill and belongs next door.

## What every template here must carry

| File | Why |
|---|---|
| `README.md` | What it does, **known limits near the top**, and a first step you can complete in about a minute |
| The paste-ready file | The actual product, in a fenced block, ready to copy with no editing beyond the slots marked for you |
| `DECISIONS.md` | What was chosen and rejected, including live disagreements |

The annotated long version is optional, and only earns its place when the
short one is not self-explaining. Where both exist, the short one is the
product and the long one is the reference.

## Adding a template

- **Size it for the smallest box it has to fit.** Standing-instruction
  fields are capped on some hosts, the caps differ by plan, and they move.
  State the measured size of your own file, which cannot date, rather than
  a host's current limit, which will.
- **Say what to cut first.** A reader who hits a cap will cut something.
  Better that you choose it than they do.
- **One copy.** If the block appears in two files it will drift. Link to it.
- **Keep it vendor-neutral in the text itself.** Host differences belong in
  the README, never in the block someone pastes.
- **Plain text, no formatting tricks.** It has to survive a textarea that
  strips markdown, collapses whitespace, or does neither.
- Sanitise before it lands here: no absolute paths, no employer-specific
  names, no internal links.
