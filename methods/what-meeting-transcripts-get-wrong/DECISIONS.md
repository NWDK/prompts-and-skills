# Decisions: what meeting transcripts get wrong

## This was a skill first

It shipped as `skills/meeting-notes`, a full triage pipeline: clean the
transcript, extract items, route them by project, propose, file, generate a
punch list. It was removed in favour of this.

The pipeline works. I use it constantly. But its own README carried seven
known limits, and read as a set they described something a stranger should
not adopt: it doesn't run out of the box, it needs a per-meeting-type
config written before first use, it assumes one export shape, it needs a
`.docx` converter that was never shipped with it, and nothing in it ever
marks an item done, so the carry-over list only grows.

A review said to fix it: add a no-filing default, make filing an optional
adapter, ship or drop the converter. Costed honestly, that's a rebuild, and
five of the seven limits survive it. Meanwhile the thing actually worth
having was four sentences buried in a Key behaviours list.

So the machinery stayed home and the findings got published. That's the
whole reason `methods/` exists.

## The headline claim got weaker on the way out, twice

The internal skill says Gemini's next-steps block "routinely misses 20-50%
of actual asks". The public README generalised that to auto-transcribers as
a class.

Both moves were wrong, and I only caught them checking the source before
publishing:

**It was one tool, not all of them.** The observation is from Gemini Meet
exports. I have not systematically tested Otter, Fireflies, or anything
else. Writing it as a fact about note-takers generally is how a true
statement about one component becomes a false statement about everything.

**It was never counted.** I went looking for the measurement behind
"20-50%" across two years of filed extracts and there isn't one. It's an
impression from repeated use. A real impression, and I'd still bet on the
direction, but a range with a percent sign on it reads as a study and
this isn't one.

So the published version names the tool, says it was noticed rather than
measured, and hands the reader a cheap way to check it on their own
note-taker instead of asking them to trust my number.

Losing the number costs less than it looks. "Re-scan the body, the summary
misses things" changes behaviour just as well as "re-scan the body, the
summary misses 20-50%", and only one of them is something I can defend.

## Four findings, not seven

The skill listed seven limits. Three of them were properties of my pipeline
rather than of transcripts: no working default, expects a note-taker export
rather than a raw caption dump, nothing marks items done. Those are real
and they're why the pipeline isn't shipped, so they're in the "what I'm not
shipping you" section rather than dressed up as findings.

The four that stayed are things about the transcripts themselves, true
whatever you build on top.

## Prime-versus-correct was the surprise

The repo has two glossary files that look redundant: one primes whisper.cpp
before it transcribes, one corrects a hosted note-taker's output after.
Checking whether that was duplication is what turned it into finding 4.
It isn't duplication. It's the same failure needing opposite fixes
depending on whether you own the transcription step, and nothing in either
file said so.
