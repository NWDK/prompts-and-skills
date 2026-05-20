# Prompt Writer

Turns messy natural-language requests into structured, copy-pasteable prompts for Claude or other models.

This is a **prompt-design skill** — it designs prompts, it does not execute the underlying task.

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
