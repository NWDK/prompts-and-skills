# What AI Meeting Transcripts Get Wrong

I've run a few hundred meeting transcripts through a triage pipeline over
about two years, mostly Gemini's Meet exports. Four things go wrong often
enough to plan around. None of them throw an error, which is the problem.

## 1. The summary block misses real asks

Read the note-taker's own summary as a starting point, then re-scan the
body yourself. Things said as asks don't reliably make it up there, and it
merges two distinct asks into one bullet, which reads tidier and loses one
of them.

The cost is an item someone was assigned in the meeting that nobody wrote
down.

Noticed over two years of Gemini exports, never counted. If you want a
number for your own note-taker, re-scan one body by hand.

## 2. Transcribers duplicate whole blocks

The same words, twice, in consecutive blocks seconds apart. It's how the
caption stream gets chunked, not something anyone said twice.

Easy to strip and easy to get wrong. Same words, consecutive, seconds
apart is also exactly what a person repeating something back to confirm it
looks like, and that's often the moment a decision got made. Flag rather
than delete when it could be real, and re-read the cleaned copy after any
meeting where people talked over each other.

## 3. Attribution is inherited, and it's confident

Whatever the transcriber decided about who was speaking, everything
downstream inherits. Two people labelled as one, or everyone collapsed into
"Speaker 1", and your action items get assigned to a confidently named
wrong person.

Worse than a gap, because a missing item looks missing and a misattributed
one looks finished. Check the speaker map before trusting any assignment,
especially with more than three people or someone who joined late.

## 4. You can prime some transcribers and not others

Whisper mis-hears names it has never seen and turns them into the nearest
ordinary English. "Smooth Matte" became "smooth Mac". "Dual price" became
"jewel price". Running it yourself, you hand it a glossary up front and it
stops guessing.

A hosted note-taker has already decided by the time you see the file. Same
failure, opposite fix: prime on the way in, or correct on the way out,
depending on whether you own the transcription step.

## The practice underneath all four

Propose before you file, and do it the same day. These are quiet wrong
answers rather than errors, so the only thing that catches them is a person
reading the output against their own memory of the meeting while that
memory still exists.

There's no ground truth here. You are the check.

## What I'm not shipping you

There's a filing pipeline under this: routing to per-project notes, a punch
list, a config per meeting type carrying speaker maps and extraction rules.
Useful to me, and it would be a bad gift. It needs that config written
before it runs at all, assumes one export shape, and never marks anything
done, so its carry-over list grows until you prune it by hand.

## Feedback

If your note-taker fails differently I'd like to know:
[open an issue](../../issues). Four findings from mostly one tool is a
narrow base.
