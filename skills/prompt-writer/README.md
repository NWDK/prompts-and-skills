# Prompt Writer

Turns messy natural-language requests into structured, copy-pasteable prompts for Claude or other models.

This is a **prompt-design skill** — it designs prompts, it does not execute the underlying task.

## Known limits

Read these before deciding whether this fits, not after.

- **It will not do the task, and that catches people out.** Paste a question while this skill is active and you get a better-worded question back, not an answer. That is the core rule working, not a bug — but if you wanted the answer, say so and drop the skill.
- **Nothing it writes is tested.** There is no eval loop, and by its own core rule the skill cannot run a prompt to find out whether it works. "Good" here means well-structured, not measured. Budget a round of real use before trusting a prompt with anything that matters.
- **It stops at the prompt boundary.** For agentic prompts it will tell you when the real problem is the context the model can see rather than the wording — and then stop. Flagging that is in scope; designing the system around it is explicitly not.
- **It is Claude-shaped by default.** The XML-tag pattern is recommended because Claude is trained on it. Prompts aimed at other models come out in the same shape, which is usually harmless but is not tuned for them.
- **It names no model versions, which means it cannot tell you what yours does.** The reasoning guidance is deliberately written to outlast individual releases, so it stops short of specifics: whether your model exposes an effort setting, what its levels are called, and whether thinking is on by default are all things you have to check against current documentation. The trade is intentional — a version list in a skill file goes stale within weeks — but the last step is yours.

## What it handles

- Writing a prompt from scratch from a vague or short ask
- Refining an existing prompt
- Designing a multi-step or agentic prompt workflow
- Writing a session handoff brief for a fresh context window
- Structuring a deep research prompt from a rough rationale
- Writing a kickoff prompt for a new build or creative task

## How to invoke it

Type `/prompt-writer` in your Claude Code session, or describe what you want and Claude will recognise the trigger phrases:

- "write me a prompt"
- "improve this prompt"
- "refine this prompt"
- "write me a handoff prompt"
- "write me a research prompt"
- "I want to kick this off"

## Key behaviours

- For simple requests: produces a prompt directly, minimal clarification
- For complex or agentic requests: asks the minimum questions needed before drafting
- Uses XML tag structure for Claude prompts (structured-tier and above)
- Does not add chain-of-thought scaffolding for models with extended thinking
- Recommends few-shot examples for any format-sensitive output

## Customise for your context

The `SKILL.md` includes a **Company/Product Guidance** section near the bottom. Fill this in with your own product terminology, roles, and workflows so the skill produces prompts that fit your context rather than generic ones.
