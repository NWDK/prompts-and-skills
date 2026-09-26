# Decisions: prompt-writer

What got chosen and rejected. Written because the same prompt was being written badly in four shapes (interactive, one-shot, sub-agent, research), each needing a different artefact.

## Executor class, never model versions

The core rule: reason about **executor class** (frontier interactive, one-shot, sub-agent, external), never named model versions. Forced: a claim naming a small model as supporting adaptive thinking was wrong within a month, and a stale version claim fails silently, no longer matching what it's aimed at. Executor class is stable: it describes the situation, not a vendor's lineup.

## Executor is orthogonal to complexity, not a version of it

Complexity tiers already existed; the instinct was to fold executor in as a tier, treating "sub-agent" as a complexity level. Wrong: a trivial task for a sub-agent still needs full self-contained treatment, since it can't ask. Collapsing the axes loses the case that bites.

## The character cap was deleted, not adjusted

An earlier version capped prompts at 8000 characters, unsourced and easy to mistake for measured. Replaced with two checkable things: **signal density** (does every line earn its place), and the destination's real input limit.

## A limit true of one surface stayed out of the public copy

One hard input limit, on one command in one tool (4000 characters, rejected outright rather than truncated), was measured and useful but stays out of the public skill: true of one surface, it would read here as a general rule. The public copy carries the general form: find the destination's limit and whether it truncates or refuses. Truncation is the dangerous one; it succeeds.

## The sub-agent section grew from two recurring failure modes

A sub-agent starts blind and usually can't ask; everything it needs must be in the prompt, not "in the project" or "obvious from context." Some harnesses allow messaging a running sub-agent, but none make it easy, so one turn is the safe assumption. Second, current models over-delegate, so the useful guidance is a **ceiling**, not encouragement: left alone they fan work out past the point where coordinating costs more than doing.

## The framing was the dated part, not the advice

An audit called this skill generic and time-sensitive. The advice held up (don't script a frontier model, don't add chain-of-thought scaffolding, effort is the dial); dated was the opening, which sold turning a messy request into a structured prompt, a 2023 problem that has largely stopped being one. It now leads with the case against using it: seeing the output and correcting it beats any prompt this would write.

## The XML claim was folklore

It said Claude "responds measurably better" to XML-tagged sections than plain paragraphs: no source, a blanket fact. Tags earn their place when a section needs referring back to, or something other than a person parses it; that reason survives a model release, tagging a three-line request doesn't.

## The self-contained brief was folded in, not published beside it

A separate template existed (cold-stranger test, exact resources, verified state, scope fence); publishing it separately would put two documents on one repo answering one question, since Session Handoff already covered the same ground, and documents on one subject drift apart. The handoff pattern absorbed what it was missing instead: the test itself, checking state claims rather than recalling them, exact names over descriptions, and the rule that a scope fence without an evidence requirement is a hope, not a control.

## Rejected

- **Naming models.** Permanently, not pending a better list.
- **A single blended complexity-and-executor scale.** Loses the trivial-task-for-a-blind-agent case, the common one.
