# What AI Meeting Transcripts Get Wrong

I've run a few hundred meeting transcripts, mostly Gemini's Meet
exports. Five things go wrong often, none an error, which is the
problem.

## 1. The summary block misses real asks

Read the note-taker's summary, then re-scan the body: asks don't
surface reliably, and two distinct ones sometimes merge into one,
losing the other.

## 2. Transcribers duplicate whole blocks

The same words, twice, in consecutive blocks: the caption stream
chunking, not something said twice. Flag, don't delete: confirming
something back looks identical, often the decision moment.

## 3. A shared mic can drop a speaker, silently

When two people share a mic, the transcriber can fold one voice onto
the other's track: no duplication, no error, just zero lines for an
attendee. Caught only by counting blocks against the invite list.

Don't attribute anything to the missing person from the text: rebuild
their items from the note-taker's structured blocks and confirm by
hand. Their silence carries no information.

## 4. Attribution is inherited, and confident

Whatever the transcriber decided about who was speaking, everything
downstream inherits it, down to a confidently wrong assignee: worse
than a gap, this looks done.

## 5. Priming works on some transcribers, not others

Whisper mis-hears unfamiliar names into ordinary English. Run it
yourself and a glossary stops the guessing; a hosted note-taker has
already decided: same failure, opposite fix.

## The practice underneath all five

Propose before you file, same day: only a person reading output
against their own memory catches these. You are the check.

## What I'm not shipping you

A filing pipeline sits under this: useful, but a bad gift, needing
setup and never marking anything done.

## Feedback

If yours fails differently: [open an issue](https://github.com/NWDK/prompts-and-skills/issues).
