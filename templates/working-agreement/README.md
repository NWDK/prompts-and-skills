# A Working Agreement With an AI Agent

Twelve clauses you paste into your assistant's standing instructions: say
when it doesn't know something, push back instead of agreeing, ask before
it builds. Nothing to install.

## Use it

Copy the block in [`SHORT-VERSION.md`](SHORT-VERSION.md) into your
assistant's standing instructions and replace the "My style" line with your
own preferences.

It's 1,487 characters, sized for the smaller settings fields.
`SHORT-VERSION.md` says what to cut if yours won't take it.

## Known limits

- Tested only inside a setup already running these rules, never pasted cold with nothing else supporting it.
- Clauses only help if you enforce them: an assistant that breaks one won't notice on its own.
- Some hosts cap the standing-instructions field below this length. `SHORT-VERSION.md` gives a cut order.

## Why

Every assistant I've used defaults to agreeable: confident guesses,
approved plans with holes in them, drafts built on an unasked question.
These are the standing instructions my own setup runs on, rewritten for
anyone else. They only work if you enforce them: point at the clause when
something gets through. Clause six tells it to challenge you, so sometimes
it will, and be wrong.

## The two files

[`SHORT-VERSION.md`](SHORT-VERSION.md) is what you paste.
[`AGREEMENT.md`](AGREEMENT.md) has the same clauses with the reason for
each: read it when a clause breaks. [`DECISIONS.md`](DECISIONS.md) is what
I chose and rejected building it.

## Feedback

Take it, change it, ignore what doesn't fit. If a clause misfires or misses
something you keep hitting, [open an issue](https://github.com/NWDK/prompts-and-skills/issues).
