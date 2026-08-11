# Meeting Notes

Turns an AI-generated meeting transcript (Gemini, Otter, Fireflies, etc.) into structured, filed action items across your projects, plus a consolidated punch list.

This is a **transcript-triage skill** — it disentangles cross-project meeting chatter into per-project notes and a shared action list, and always proposes routing before it files anything.

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

Start from `variants/example.md` (a team-sync variant template with a neutral punch-list HTML template) and `glossary-corrections.md` (a starter glossary pattern).
