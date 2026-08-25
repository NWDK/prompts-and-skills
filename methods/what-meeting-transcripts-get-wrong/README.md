# What AI Meeting Transcripts Get Wrong

I've run a few hundred meeting transcripts through a triage pipeline over
about two years, mostly Gemini's Meet exports. Four things go wrong often
enough to plan around. None of them throw an error, which is the problem.

If you take one thing: the summary block at the top is a hint, not a record.

## 1. The summary block misses real asks

Every note-taker writes its own summary and action-item block. Read it as a
starting point and then re-scan the body yourself, because things said as
asks don't reliably make it up there. It also merges two distinct asks into
one bullet, which reads as tidier and loses one of them.

**How I know:** noticed consistently across Gemini Meet exports over about
two years. I have never counted it, and my working impression of "a fifth
to a half of them" is an impression, not a measurement. The direction is
solid, the number isn't mine to give you. If you're relying on your
note-taker's summary today, the cheap test is to re-scan one body by hand
and see what you find.

**What it costs:** the missed item was assigned to someone in the meeting
and nobody has it written down.

## 2. Transcribers duplicate whole blocks

Auto-transcribers emit the same words twice, in consecutive blocks, seconds
apart. It's an artifact of how the caption stream gets chunked, not
something anyone said twice.

Stripping it is easy to describe and easy to get wrong. The rule that
catches it, same words plus consecutive plus seconds apart, is exactly the
shape of a person repeating back what was just said to confirm it. Which
happens constantly in meetings, and is often the moment a decision got
made.

**What to do:** strip it, but flag rather than delete when the repetition
could be real, and re-read the cleaned copy after any meeting where people
talked over each other.

## 3. Attribution is inherited, and it's confident

Whatever the transcriber decided about who was speaking, everything
downstream inherits. If it labels two people as one speaker, or collapses
everyone into "Speaker 1", your action items get assigned to a confidently
named wrong person.

This one is worse than a gap because it produces a plausible artifact. A
missing item looks missing. A misattributed one looks finished.

**What to do:** check the speaker map before you trust any assignment,
especially on calls with more than three people or where someone joined
late.

## 4. You can prime some transcribers and not others

Whisper mis-hears names it has never seen, and turns them into the nearest
ordinary English. "Smooth Matte" became "smooth Mac". "Dual price" became
"jewel price". Running it yourself, you can hand it a glossary up front and
it stops guessing.

You can't do that with a hosted note-taker. It has already decided by the
time you see the file, so the same problem needs a corrections pass on the
way out instead of a priming pass on the way in.

Same failure, two different fixes, and which one you get depends on where
the transcription happened. Worth knowing before you build the wrong one.

## The practice underneath all four

Propose before you file. Every one of these is a quiet wrong answer rather
than an error, so the only thing that reliably catches them is a human
reading the proposed output against their own memory of the meeting, while
that memory still exists. Do it the same day.

That's also the honest limit of any pipeline built on this. There's no
ground truth to check against. You are the check.

## What I'm not shipping you

I have a filing pipeline built on top of this: routing to per-project
notes, a punch list, a per-meeting-type config carrying speaker maps and
extraction rules. It's genuinely useful to me and it would be a bad gift.
It needs a config written before it runs at all, it assumes one export
shape, and it never marks anything done, so its carry-over list only grows
until you prune it by hand.

The findings above are the part that transfers. The machinery is shaped by
my projects, not yours.

## Feedback

If your note-taker fails differently, I'd like to know:
[open an issue](../../issues). Four findings from mostly one tool is a
narrow base, and the scoping in finding 1 is exactly the kind of thing
someone else's experience would sharpen.
