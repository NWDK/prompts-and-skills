# Decisions: what meeting transcripts get wrong

## This was a skill first

It shipped as a full triage pipeline: clean, extract, route, file,
punch list. Removed in favour of this. It works, but its own README
carried seven known limits that, together, described something a
stranger shouldn't adopt: config needed first, one export shape
assumed, nothing ever marked done. The machinery stayed home; the
findings got published. That's why `methods/` exists.

## Noticed, not measured, and named

The findings come from one tool's exports and were never counted, so the
piece names the tool, says noticed rather than measured, and gives no
percentage. A reader checks their own note-taker instead of trusting a
number that was only ever an impression.

## Five findings, not seven, not four

The original listed seven; three were properties of my pipeline, not of
transcripts, and sit under "what I'm not shipping you" instead. A fifth
joined later: the shared-microphone collapse, previously a procedural
check, not a described failure. Far more severe than the attribution
finding: not a missing voice but one never recorded, with no error to
notice by. Its own entry is earned because the fix differs: attribution
needs the speaker map checked, this needs the attendee list.

## Prime-versus-correct was the surprise

Two glossary files that look redundant: one primes a local transcriber
before it runs, one corrects a hosted note-taker's output after. Not
duplication: the same failure needing opposite fixes, depending on who
owns the transcription step.
