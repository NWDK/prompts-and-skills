# Triangulate Load-Bearing Facts

The most expensive thing an AI assistant does to you is quiet. It picks up
a number, treats it as settled, and builds on it. Weeks later the work rests
on something nobody ever checked.

This is one rule for stopping that.

## What goes wrong

Someone in a meeting says "oh, ninety-nine percent of them". They mean
*most*. The transcript says 99%, so the assistant says 99%, and from then
on 99% is a fact. It appears in the summary, then the plan, then the
recommendation. Nobody lied and nothing errored.

The same thing happens with a figure lifted from a report without its
surrounding context, or a number that was true when it was measured and has
moved since.

What makes it expensive is that it hardens out of sight. By the time the
number is load-bearing it has been repeated enough times to look
established, and the thing you would check it against is three documents
back.

## The rule

Before a fact becomes load-bearing, corroborate it from two other sources.

A fact is **load-bearing** when future work rests on it being right. Not
when it is interesting, not when it is quoted. When a decision changes
direction because of it, when it becomes a threshold or a constant, when
it goes into a brief someone else will act on.

Most facts never reach that bar. The habit that catches the ones that do is
asking, at the point a fact starts doing work: *if this is wrong, what
breaks?* If the answer is "the plan", triangulate it.

## Ask for it directly

You do not need any setup. In the conversation:

> Before we build on that, treat it as a load-bearing fact. Find two
> independent sources for it, tell me what they are, and tell me if you
> can't.

Without that last clause you get two sources whether or not two exist.

## What "independent" actually means

This is where it usually fails, and it fails in a way that feels like
success.

**Two models agreeing is not two sources.** Ask the same question twice and
you often get the same answer from the same underlying page. I once had two
research passes agree confidently, and the agreement dissolved on
inspection: they were citing the same handful of pages at each other, and
one claim turned out to be a single blog post wearing five different URLs.

**Two runs of the same tool are not independent.** Neither are two
documents from the same author, or a report and the press release it was
written from.

**Precise notation is not evidence of precision.** A number carried to two
decimal places is not better sourced than a round one. It just looks it.

So the test is not "did I get two answers". It is: could these two have
been wrong in the same way? If yes, you have one source.

## When you can't corroborate it

Sometimes there is genuinely only one source. That is a finding, not a
failure, and the answer is not to go looking harder until something turns
up.

Use it, and mark it. Say in the document that it rests on one source and
name what would confirm it. Then keep it soft: let a single-source fact
lean a decision, never gate one. The failure to avoid is a hard threshold,
a go/no-go, or a constant in code resting on something one person said once.

## The one that got me

A measured ratio, pulled from a dashboard that logged three successive
readings and an explicit note that it would keep falling. It got extracted
as a fixed constraint, repeated across about eight documents, and written
into four separate briefs that other people acted on.

When it was finally checked against source data, the real figure was a
small fraction of the one being quoted. The original source had been right
the whole time, and had even predicted the change. Nothing had gone wrong
except that a moving number got quoted as a fixed one, and then quoted
from the quote.

That is the shape to watch for. Not a wrong fact. A fact that stopped being
current while everything downstream kept treating it as though it were.

## If you do formal research passes

The same rule scales up, with one addition worth knowing. When you run a
research question across more than one model, reconcile the claims by where
the evidence came from rather than by whether the reports agree. Agreement
from a shared lineage is not corroboration, and labelling it honestly
dissolves a surprising amount of the apparent confirmation in a typical
pass.

## Feedback

If this misfires, or you find a failure shape it misses:
[open an issue](../../issues).
