# Meeting Notes

Turns an AI-generated meeting transcript (Gemini, Otter, Fireflies, etc.) into structured, filed action items across your projects, plus a consolidated punch list.

This is a **transcript-triage skill** — it disentangles cross-project meeting chatter into per-project notes and a shared action list, and always proposes routing before it files anything.

## Known limits

Read these before deciding whether this fits, not after.

- **It does not run out of the box.** There is no working default variant, only a template. Pre-flight halts when `variants/<variant>.md` is missing, so writing one is the first job — budget that before your first transcript rather than during it.
- **It expects a note-taker's export, not a raw transcript.** The pipeline assumes the shape those tools emit: a summary block, a decisions block, a timestamped body. A bare caption dump, or a tool whose export you have not taught it, halts at pre-flight by design.
- **Missed action items fail silently.** The skill treats the transcriber's own summary as incomplete and tells you to re-scan the body — but nothing checks the re-scan, and there is no ground truth to check it against. The failure mode is a quiet omission, not an error. Read the routing proposal against your own memory of the meeting.
- **Assignees are only as good as the transcript's speaker labels.** Attribution is inherited wholesale from the export. If your transcriber mislabels who said what, or collapses everyone into "Speaker 1", the proposal will confidently name the wrong person.
- **Echo-stripping is a heuristic and can eat real dialogue.** The rule that catches phantom captions — same words, consecutive blocks, seconds apart — also matches someone genuinely repeating back what was just said. There is an escape hatch (`[possible echo]`), but firing it is a judgement call, so re-read the cleaned transcript after a meeting where people talked over each other.
- **Screenshot extraction needs a companion document, and a converter this repo does not ship.** Step 4 runs only when a `.docx` or similar sits beside the transcript, and it assumes you already have a way to convert that file and pull the embedded images out. No tool here does it. Anything shared on screen but never captured into that document is gone.
- **Nothing ever marks an item done.** The example variant carries unfinished work forward by scanning the previous extract for items "not marked done" — but no step in the pipeline marks anything done, so that has to become your habit or the carry-over list only grows. The optional current-state snapshot is overwritten from the meeting in front of it, so an item still open but not raised this time drops out of it entirely.

## What it handles

- Cleaning the transcript (strips the duplicated "phantom echo" artifact common to auto-transcribers; applies your glossary corrections)
- Extracting action items, decisions, and open questions — re-scanning the body, not trusting the transcriber's own summary
- Routing each item to the right project and proposing it for your approval
- Filing per-project meeting-extract notes
- Optionally refreshing a coordination "current-state" snapshot and generating a punch-list HTML

## How to invoke it

Type `/meeting-notes <path>` in your Claude Code session, or drop a transcript into your inbox folder and say:

- "process the transcript"
- "triage the meeting notes"
- "extract action items from this call"

## Key behaviours

- **Propose-then-stop:** never files anything until you confirm the routing proposal
- **Variant-driven:** each meeting type (team sync, customer call, dev standup) gets its own config file with its own routing table and output format
- **Re-scans the body:** treats the transcriber's "next steps" block as a hint, not ground truth (auto-passes miss 20–50% of real asks)
- **Never auto-publishes:** handing off the punch list to a live URL is always your explicit call

## Customise for your context

Four `CUSTOMIZE` blocks in `SKILL.md` mark what depends on your setup:
1. **Variants** — your meeting types and their config files
2. **Glossary** — the misspellings your transcriber makes (see `glossary-corrections.md` for the pattern)
3. **Filing destinations** — where per-project extracts land
4. **Publishing** — your publish step, if any

Start from `variants/example.md` and `glossary-corrections.md` (a starter glossary pattern).

**The variant is the real work, and it is bigger than a routing table.** It carries the speaker-identity map, the extraction rules for that meeting type, and the shape patterns that mislead a naive pass — a thin variant is the most common reason this skill underdelivers. `SKILL.md` ends with an "Adopting this skill in another workspace" section splitting what transfers from what you have to write.
