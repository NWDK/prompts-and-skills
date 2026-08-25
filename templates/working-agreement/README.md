# A Working Agreement With an AI Agent

A template, not an installable skill. Nothing to install, no tooling, no
particular vendor: twelve clauses you paste into your assistant's standing
instructions, and one habit that keeps them alive.

## Use it now

1. Open **[`SHORT-VERSION.md`](SHORT-VERSION.md)** and copy the block.
2. Paste it into your assistant's custom instructions, project instructions,
   or system prompt.
3. Replace the "My style" line with two or three preferences you actually
   hold.

That is the whole setup. The block is sized to fit the smaller
standing-instruction fields, and `SHORT-VERSION.md` says what to cut first
if yours still refuses it.

Then enforce it once. The first time an unlabelled guess or a rubber stamp
shows up, point at the clause it broke. You should notice the difference in
the first session: more "I don't know, and here is what would settle it",
more numbered questions before drafts, and at least one plan of yours
getting pushed on.

## Why this exists

I'm Nick. I run a lot of my work through AI assistants, and these are the
actual standing instructions my own setup runs on, rewritten so they make
sense outside it.

They exist because the default behaviour of every assistant I have used is
agreeable, and agreeable fails in predictable ways: confident guesses
instead of "I don't know", approval instead of scrutiny, and
finished-looking drafts built on questions that were never asked.

The fix was not better prompting tricks. It was an explicit agreement that
makes the uncomfortable behaviours the job: say what you don't know, push
back, ask before building. The centre of gravity is one idea: **truth
first, agreeableness never**.

## Known limits

- **It only works if you enforce it.** An agreement your assistant violates
  without consequence decays into decoration within days. The habit that
  keeps it alive: when a guess slips through, name the clause it broke.
- **Pushback is a feature you have to want.** Clause six instructs the
  assistant to challenge you, and it will sometimes challenge you when it is
  wrong. That trade is the point, but it is a trade; if you want an
  assistant that only agrees, this agreement is not for you.
- **These are my defaults, not laws.** They came out of one person's working
  life. The style section is explicitly yours to rewrite, and any clause
  that fights how you work should lose the fight.
- **A standing instruction is not a guarantee.** Models drift, forget, and
  occasionally ignore instructions, especially in long conversations. The
  agreement raises the floor substantially; it does not make verification
  optional, and clause one never stops being your job too.
- **I have not tested it on every host.** It is plain text with no
  formatting tricks, so it should paste anywhere, but the only surfaces I
  use daily are my own. If it misbehaves on yours, that is worth an issue.

## The two files

**[`SHORT-VERSION.md`](SHORT-VERSION.md)** is the product: twelve numbered
lines, one paste, a style slot to personalise.

**[`AGREEMENT.md`](AGREEMENT.md)** is the same agreement annotated, every
clause with the reason it exists. That matters because you will only enforce
the clauses whose point you can feel. Read it in week two, when a clause
gets violated and you need its reasons to decide whether to enforce it or
delete it.

The clauses cover inventing information (including the two sneaky forms:
guessing look-up-able values, and stating absences off one failed search),
pushing back on weak plans, asking material questions before delivering,
communication that respects your time, writing in your voice without
inventing your life, and matching effort to stakes.


## Who this is for

Anyone who uses an AI assistant for real work: writing, deciding, building,
researching. If you have ever caught your assistant confidently making
something up, agreeing with a plan you later found holes in, or asking the
key question underneath the draft it already wrote, these clauses are aimed
at exactly those moments.

## Where this came from

These clauses are the load-bearing subset of the collaboration rules my own
workspace auto-loads into every session, plus the truth-handling rules that
earned their place through repeated failures: the guessed value that read
exactly like a real one, the "it isn't there" that meant "I searched wrong",
the bio line that implied more than the facts. The full rewrite reasoning,
including what was deliberately left out and why, is in
[`DECISIONS.md`](DECISIONS.md).

## Feedback

If a clause misfires with your assistant, reads as ambiguous, or is missing
the failure you keep hitting, open an issue or send a PR. This is the piece
here most likely to be shaped by other people's working lives,
and I would like it to be.
