# Three Gates and a Lock

How to approve work you can't personally re-derive.

I direct agents to build things I can't audit line by line, like a
design system whose components all have to be right, faster than I could
check. A "checklist, mark it done" pass grades its own work: blind where
it was blind while producing it.

## Gate 0: a pre-flight that clears nothing

Before the three gates, run the cheap deterministic checks and stop:
write nothing, mark nothing. It gives the worker fast feedback instead
of two expensive gates catching what a script catches in seconds. It
can't satisfy gate 2: it isn't independent, and gates 2 and 3 re-check
everything anyway.

## Gate 1: semantic. Does it mean the right thing?

Intent, naming, content: is this the right thing, for the case it
serves? It runs first because it's allowed to make changes: verifying
intent reworks the thing, so rework happens before the passes that check
it. A structural check verifies wiring, never truth.

## Gate 2: independent QA. Fresh eyes, no approval to write

A second pass, in a fresh session, checking against everything that has
to hold true.

**It runs separately** (self-check is what this prevents), and **it
doesn't write the approval**: a tick to produce is a stake in passing. Once its full
verdict is written and delivered, and the owner says go, it may fix what
it found; a fresh session re-checks the fix. Clearance is version-tied; any change voids it.

## Gate 3: mechanical. Does it actually do the thing?

The deterministic checks, then the marker: last, because it's the lock.
A defect found here stops and gets reported, never fixed inline.

## The lock: approved means frozen

Once something carries the marker, nothing modifies it without an
instruction naming that item. Without this the gates are decorative:
verified work can quietly stop being correct when downstream edits it in
good faith.

Three properties: **survives permissive modes**, **sub-agents inherit
it** and escalate rather than decide, and **authorisation is narrow**:
named item, this session, this change.

**Reopening it needs a reason from outside itself**: changed code, a
missing capability, a measurable defect, or a named instruction.
"Internal consistency" isn't enough: an argument that never leaves the
artefact can be thorough and still answer a question nobody asked.
Waived is recorded; silently skipped is a false clearance.

## What convinced me

I reordered these gates because two QA runs over four **already
approved** components found defects in all four.

- A struck-through price existed only on demo screens: the component
  rendered it unstruck.
- A fix for one check broke another.
- No developer note, despite live wiring.
- A property was dead on twelve of sixteen variants; three screens
  showed quantity twenty against a setting of one.

The fourth was held back for its own QA, the only reason anyone caught
it, already live in three places. Approval had gone out first.

## Cost

This doesn't add a step if you were already doing QA: it moves approval
to the end, so a finding blocks it, instead of arriving after.

## Feedback

If it fails differently for you: [open an issue](https://github.com/NWDK/prompts-and-skills/issues).
