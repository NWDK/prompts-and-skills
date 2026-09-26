# Triangulate Load-Bearing Facts

The most expensive thing an AI assistant does to you is quiet: it picks
up a number, treats it as settled, and builds on it. Weeks later the
work rests on something nobody checked. This is one rule for that.

## What goes wrong

Someone in a meeting says "oh, ninety-nine percent of them," meaning
*most*. The transcript says 99%, so the assistant does, and it's now a
fact: the summary, the plan, the recommendation. Nobody lied or errored.

## The rule

Before a fact becomes load-bearing, corroborate it from two sources.

A fact is **load-bearing** when future work rests on it being right: a
decision changes direction, or it becomes a threshold, a constant, a
brief someone acts on.

Ask, at the point it starts doing work: *if this is wrong, what
breaks?* If the answer is "the plan," triangulate it.

## Ask for it, and check what comes back

No setup needed:

> Before we build on that, treat it as a load-bearing fact. Find two
> independent sources for it, tell me what they are, and tell me if you
> can't.

Without that last clause you get two sources whether or not two exist.
Check the number too: an export can read complete while the actual
figure, once a chart, is gone.

## What "independent" actually means

This is where it usually fails. **Two models agreeing is not two
sources**, since asking twice often finds the same page. **Two runs of
the same tool aren't independent**, neither are two documents from one
author. **Precise notation isn't evidence of precision**: two decimals
aren't better sourced than round, they just look it.

The test isn't "did I get two answers." It's: could these two have been
wrong the same way?

## When you can't corroborate it

Sometimes there's genuinely one source: a finding, not a failure. Use
it, mark it, keep it soft. A single-source fact can lean a decision,
never gate one.

## The one that got me

A ratio pulled from a dashboard that logged three falling readings got
extracted as a fixed constraint and written into briefs people acted
on. The real figure, checked against source, was a small fraction of
the one quoted, and the source had predicted the change all along. Not
a wrong fact: one that stopped being current while everything
downstream kept treating it as though it were.

## If you do formal research passes

The rule scales up: reconcile claims by where the evidence came from,
not whether reports agree. A shared lineage isn't corroboration.

## Feedback

If this misfires, [open an issue](https://github.com/NWDK/prompts-and-skills/issues).
