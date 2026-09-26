# Sanitize for Sharing

Strips private context out of an internal document (a skill, a prompt, a
process file) before it goes public: names, paths, URLs, and
workspace-specific sections become generic placeholders. Returns a change
summary alongside the sanitized file, so a human can see what moved
before anything ships.

## See it work

[`example/`](example/) is a synthetic file with problems planted in it,
and what this produces from it: what got caught, what it left alone, and
the credential on line 37 that passes straight through untouched.

[`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md) is the second pass: it
checks the exact files you're about to ship, not the words in one of
them.

## Known limits

- **This rewrites content. It is not a release gate.** It looks at the
  words in one file. What it never sees: git history, hidden files, image
  metadata, credential patterns, what code does on the network, licences,
  privately-resolving links, and whether the cleaned-up thing still works.
  A separate audit covers this, over the files that ship.
- **A full release audit finds real defects sanitising never will**: it
  checks names and paths, not whether a claim is true or a command runs.
- **Detection is a checklist, and checklists age.** It catches names,
  paths, emails, and internal references, not an industry-identifying
  example or a one-person quote. Those need the change summary's human
  reader.
- **Over-sanitising is a real failure too.** A document stripped of every
  proper noun stops teaching anything. Public tool and model names, and
  standard technical terms, stay.

## Use this now

1. Point your agent at `SKILL.md` in this folder.
2. Give it one document: "sanitize this for sharing."
3. Read the change summary before the sanitized file: it's where
   judgement calls are flagged, and where leaks live.

Then run the second gate, [`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md),
over the exact staged file set, not the working tree.

## Where this came from

Reasoning behind the two-gate split, the placeholder style, and what's
still open: [`DECISIONS.md`](DECISIONS.md).

## Feedback

If a detection class misses something, or the placeholder conventions
fight your document's shape, open an issue or send a PR.
