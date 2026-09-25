# Prompt Writer

Designs a prompt instead of answering the question. Paste it a messy ask and you get a prompt back, not a result.

## When it's worth using

Most of what got called prompt engineering has stopped paying: current models do better with a goal and constraints than a script. If you can see what comes back, ask for the thing and correct it. That beats any prompt this would write.

It earns its keep where correcting it isn't available: a handoff to a fresh context, a sub-agent brief, an unattended or one-shot run, or a deep-research prompt where you don't see the middle. Not one of those? You probably don't need it.

Newer to prompting? Start structured and loosen once you trust the model; the executor table is the part to loosen first.

## Known limits

Won't do the task. Paste a question and you get a better-worded question back.

Nothing it writes is tested. There's no eval loop, and by its own core rule it can't run a prompt to check whether it works. "Good" here means well-structured, not measured.

Stops at the prompt boundary. For agentic prompts it flags when the real problem is the model's context, not the wording, then stops.

Names no model versions, deliberately. Thinking defaults, effort ranges and parameter names move fast; check your model's current docs where it matters.

## Use it

Copy the folder into your `skills/`, or paste `SKILL.md` into a project's custom instructions. Ask for a handoff, research, or sub-agent prompt.

`SKILL.md` has three worked patterns: session handoff, deep research, and kickoff. The handoff pattern carries the test worth stealing even if you ignore the rest: could a cold stranger act on this without asking anything or looking anything up?

[`DECISIONS.md`](DECISIONS.md) has what got chosen and rejected, including the capability claim that went stale within a month, which is why this names no model versions.

## Customise it

`SKILL.md` has a **Company / Product Guidance** section near the bottom. Fill it in with your own terminology, roles and workflows, or the prompts come out generic.
