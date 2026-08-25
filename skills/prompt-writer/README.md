# Prompt Writer

Designs a prompt instead of answering the question. Paste it a messy ask
and you get a prompt back, not a result.

## Read this first, it might talk you out of it

Most of what got called prompt engineering has stopped paying. Current
models do better with a goal and the constraints than with a script, and a
prompt written prescriptively for an older model measurably lowers the
output quality of a newer one. If you're in a conversation and can see what
comes back, ask for the thing and correct it. That beats any prompt this
would write for you.

What still pays is the case where correcting it isn't available, because
the prompt has to carry everything:

- **Handing off to a fresh context.** A new session, a worktree, a new
  window after a long one ended.
- **Briefing a sub-agent.** It starts from your prompt and little else.
- **Unattended or one-shot runs.** Overnight, batched, scheduled. No second
  turn to correct course.
- **Deep research.** The shape of the question decides the shape of what
  comes back, and you don't see the middle.

That's where I use it now. If your case isn't one of those four, you
probably don't need this.

There's a fifth, and it's about you rather than the model: if you're newer
to this and want a tighter leash while you get a feel for what these models
do unprompted, start structured and loosen it. The skill's executor table
is the part to loosen first.

## Known limits

It won't do the task. Paste a question while this is active and you get a
better-worded question back. If you wanted the answer, say so and drop the
skill.

Nothing it writes is tested. There's no eval loop, and by its own core rule
it can't run a prompt to find out whether it works. "Good" here means
well-structured, not measured.

It stops at the prompt boundary. For agentic prompts it will tell you when
the real problem is the context the model can see rather than the wording,
and then stop.

It names no model versions, deliberately. Thinking defaults, effort ranges
and parameter names have all moved in the last few releases, so anything
specific here would be wrong by the time you read it. Where it matters,
check your model's current docs.

## Use it

Copy the folder into your `skills/`, or paste `SKILL.md` into a project's
custom instructions. Then ask for a handoff prompt, a research prompt, or a
sub-agent brief.

`SKILL.md` has three worked patterns for the cases above: session handoff,
deep research, and kickoff. Those are the parts to read.

The handoff one carries the test worth stealing even if you ignore the rest:
could a cold stranger act on this without asking anything or looking
anything up?

[`DECISIONS.md`](DECISIONS.md) is what got chosen and rejected, including
the capability claim that was wrong a month after I wrote it, which is why
this names no model versions.

## Customise it

There's a **Company / Product Guidance** section near the bottom of
`SKILL.md`. Fill it in with your own terminology, roles and workflows, or
the prompts come out generic.
