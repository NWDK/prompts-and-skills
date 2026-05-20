# Prompts and Skills

A collection of reusable prompt skills for Claude Code.

Each skill is a structured markdown playbook that tells Claude how to approach a specific type of task. Drop a skill into your Claude Code workspace and invoke it with `/skill-name`.

## What is a skill?

In Claude Code, a skill is a `SKILL.md` file that loads into the agent's context when you invoke it. It defines operating modes, design patterns, and guardrails for a specific task type — so you don't have to re-explain your approach every session.

## How to use a skill

1. Copy the skill folder (e.g. `skills/prompt-writer/`) into your own `skills/` directory.
2. Add an entry for it in your `skills/INDEX.md` so Claude knows it exists.
3. In your `CLAUDE.md`, add a trigger rule pointing to the skill (e.g. "Prompt design or refinement: load `skills/prompt-writer/SKILL.md`").
4. Invoke it in a session by typing `/prompt-writer` (or whatever the skill name is).

If you don't have a full workspace setup, you can also paste the `SKILL.md` content directly as a custom instruction in Claude.ai Projects — it works without the folder infrastructure.

## Skills

| Skill | What it does |
|---|---|
| [prompt-writer](skills/prompt-writer/) | Design or refine prompts without executing the underlying task |

## Notes

- Each skill folder contains a `SKILL.md` (the file Claude reads) and a `README.md` (human-readable summary).
- Skills are intentionally generic. Customize the Company/Product Guidance section in each skill for your own context.
- These are written for Claude Code but the instructions are plain enough to adapt for other models.
