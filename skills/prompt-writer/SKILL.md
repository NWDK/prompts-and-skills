---
name: prompt-writer
description: Design or refine prompts without executing the underlying task. Use when the user wants a prompt written from a messy request, an existing prompt improved, a multi-step prompt or agent workflow structured, or a session handoff brief written for a fresh context window.
---

# Prompt Writer

## Purpose

Use this skill when the user wants to:

- create a prompt from a messy or short request
- improve an existing prompt
- design a prompt workflow or agent setup
- turn an idea into a copy-pasteable prompt for another model or tool
- write a session handoff or fresh-context brief for a new agent

This skill is not for executing the underlying task itself.

## Core Rule

Never answer, research, summarise, code, or complete the user's real task when this skill is active.

Only return:

- a prompt
- a prompt set
- a prompt workflow
- brief notes explaining prompt-design choices when useful

## Operating Modes

Classify each request into one of these four modes:

1. `write-from-scratch`
   The user gives a vague, short, or messy natural-language ask.

2. `refine-existing-prompt`
   The user pastes a draft prompt and wants it improved.

3. `design-workflow-or-agent`
   The user wants a multi-step, tool-using, or agentic prompt setup.

4. `handoff-or-context-brief`
   The user wants a fresh-context prompt for a new agent session — either to hand off a current project or to kick off a subtask in a clean context window.

## Complexity Tiers

Before drafting, identify which tier the prompt sits at. Use only as much structure as the tier needs.

| Tier | What it is | Key elements |
|---|---|---|
| Quick | Single conversational exchange, low stakes | Clarity + output format only |
| Structured | Specific output, domain knowledge, or accuracy matters | Role + context + XML structure + examples |
| Chained | 2–5 step pipeline, intermediate outputs used downstream | Prompt-per-step, clear handoffs, stop conditions |
| Agentic | Tool use, decisions, loops, sub-agents | Context design + spawn criteria + scope gates + stop conditions |

## Executor

Complexity describes the task. This describes who runs it. The two are independent, and the executor changes the draft more than the tier does — the same Structured-tier task written for a frontier model and for a sub-agent should not look alike.

| Executor | How to point it |
|---|---|
| **Frontier model, interactive** — you see the output and can iterate | Goal, constraints, definition of done. No step-by-step scripts. Prompts written prescriptively for older models measurably reduce output quality on current frontier models; the model's own plan is usually better than a hand-written one. |
| **Frontier model, one-shot or unattended** — overnight run, batch job, scheduled agent | Same shape, plus explicit stop conditions, exclusions, and what "done" means. There is no second turn to correct course, so close the exits rather than scripting the route. |
| **Sub-agent** — spawned into a fresh context by an orchestrator | Explicit to the point of feeling redundant. It shares none of your context, cannot ask a clarifying question, and will not generalise an instruction you gave for only one case. Every path, input, constraint, and output shape goes in the prompt. |
| **External system** — another vendor's model, or a hosted research or agent product | Point precisely: one pointed question, sources to prefer or avoid, the output shape you want back, and how to handle uncertainty. One shot, and no visibility into what it did. |

The failure modes sit at opposite ends of the same axis. Over-specifying a frontier model costs you quality; under-specifying a sub-agent or an external system costs you the run.

When the executor is unstated and the tier is Structured or above, ask. It is the single input most likely to change the draft.

## Default Behavior

1. For quick-tier requests, produce an improved prompt directly with minimal or no clarification.
2. For structured-tier and above, ask only the minimum questions needed to pin down: goal, inputs, audience, output format, constraints, executor (see below), stakes.
3. If the user already pasted something that looks like a prompt, do not answer it. Refine it.
4. Default to one strong primary prompt. Add variants only when they materially help.

## Prompt Design Pattern

Use this pattern internally when drafting. Wrap sections in XML tags for any structured-tier prompt or above — Claude is trained on this structure and responds measurably better to it than plain paragraphs.

```
<role>...</role>
<task>...</task>
<context>...</context>
<examples>...</examples>          <!-- include for format-sensitive or accuracy-critical outputs -->
<output_format>...</output_format>
<stop_conditions>...</stop_conditions>
```

Quick-tier prompts do not need XML tags.

## Reasoning and Effort

Reasoning is no longer a feature you switch on. On current frontier models it is adaptive by default, and on the most capable ones it cannot be disabled. Design around it rather than for it:

- **Never add "think step by step", a `<reasoning>` block, or manual chain-of-thought scaffolding.** The model reasons internally; the scaffolding competes with it and can degrade the result.
- **Prompt for outcomes, not steps.** In agentic prompts, let the model think between tool calls instead of scripting the sequence.
- **The dial is effort, not thinking.** Where the target exposes an effort level, that is the intelligence / latency / cost control — recommend a level instead of trying to shape reasoning depth in prose. Low for scoped or latency-sensitive work, high as a general default, the top levels for hard agentic and coding work. Pick the level from the task rather than defaulting to the maximum.
- **Do not hardcode model versions.** Reason about the executor class above. Thinking defaults, effort ranges, and parameter names have all changed within the last few releases, so a version list in a skill file goes stale within weeks. Name a version only where behaviour genuinely differs, and verify it against current releases before relying on it.

## Few-Shot Examples

Include worked examples in any prompt where format, tone, or precision matters — not just safety-critical ones. Two to three labeled examples are usually enough. Place them inside `<examples>` tags so the model reads them as demonstrations, not as live tasks.

When examples are the most important quality lever, say so in the prompt-design notes.

## Common Patterns

These are the three prompts most frequently needed. Apply the relevant design notes when the request matches.

### Session Handoff / Fresh-Context Brief

Used when wrapping up a session and spinning up a new agent to continue work in a clean context window.

Key elements to include:
- Current state: what is done, what is outstanding, any decisions made this session
- Target scope: what the new agent should work on (full project, subtask, or specific question)
- Essential context: relevant file paths, constraints, conventions, or decisions the new agent must know
- Kickoff instruction: what to do first

Design notes:
- Keep it tight — a handoff that tells the agent to read every session note defeats the purpose
- Use `<current_state>`, `<outstanding_work>`, `<context>`, `<your_task>` XML tags
- Ask before drafting: full project handoff or scoped subtask? These need different levels of context

### Deep Research Prompt

Used when starting a serious investigation and wanting rough rationale sharpened into a structured research prompt.

Key elements to include:
- Research question (specific, not open-ended — the most common gap to fix)
- Rationale or angle (why this matters, what you already believe or suspect)
- Output type (synthesis, comparison, gap analysis, recommendations, raw findings)
- Depth guidance (broad survey vs deep dive into one area)
- How to handle gaps or uncertainty

Design notes:
- Turn the vague topic into a pointed question first — this is usually the highest-value edit
- Recommend a high effort level where the target exposes one; research is the case that repays it
- Always include a no-fabrication rule and instruct the model to flag uncertainty explicitly
- If sources matter, add guidance on what to prioritise or avoid

### Kickoff / Build Prompt

Used when starting something new — a document, design brief, plan, feature, or creative piece.

Key elements to include:
- What is being built and for whom
- Project or product context the model needs
- Style, tone, or format constraints
- What done looks like (the deliverable)
- What not to do (explicit exclusions)

Design notes:
- Decide upfront whether the prompt should invite clarifying questions or dive straight in — ask if unclear
- For creative work, include a brief example or reference that captures the desired style
- For technical builds, state the stack, conventions, or prior art explicitly

## Context Engineering Note

For agentic-tier prompts, prompt wording is often less important than what context the model has access to: prior memory, tool results, documents, past decisions. Before finalising an agentic prompt, surface whether the context design (what information is fed in) is adequate. A well-structured prompt in a thin context still fails.

This is the prompt-writer's scope boundary: flag the question, do not architect the system.

## Sub-Agents (Agentic Mode)

When writing an orchestrator prompt, the prompt must include criteria for sub-agent use:

- when to delegate (what triggers a sub-agent vs handling inline)
- what scope and goal each sub-agent gets
- stop and handoff conditions
- what the orchestrator does with sub-agent output

Two things matter more than that list, and are the usual reason delegation goes wrong:

- **The sub-agent starts blind and cannot ask.** It shares none of the orchestrator's context, conversation, or working assumptions, and has no way to raise a clarifying question — ambiguity a person would resolve in one exchange becomes a silent wrong turn instead. Everything it needs goes in its prompt. This is the one place where more explicit is reliably better.
- **Current models over-delegate, so orchestrator prompts usually need a ceiling rather than encouragement.** Every sub-agent re-establishes context, re-explores, reports back, and the orchestrator then re-reads the report; that overhead is real and it repeats. Write the prompt to delegate only where the work is genuinely independent and sizeable, to keep spawn counts low, and to commit to a sub-agent's findings rather than re-deriving them. Verification belongs in the orchestrator's own loop, not in a spawned checker.

If your workspace has multi-agent conventions, reference them here rather than re-documenting them in the prompt itself.

## Output Rules

1. Wrap each final prompt in triple backticks.
2. Keep commentary outside the prompt block.
3. Keep prompt-design notes concise and focused on decisions that materially change behaviour.
4. After delivering a prompt, invite iteration with a short follow-up.
5. Length is governed by signal density, not a character count. Cut what does not change behaviour, then stop — there is no model-side length limit worth designing around, and a numeric cap starves reasoning on hard tasks.
6. Check the destination for a hard input limit before delivering. Slash-command fields, form inputs, and some agent-config surfaces either reject or silently truncate, and a correct prompt that gets clipped is worse than a shorter one. Where a limit applies to a surface used often, record the number in the guidance section below rather than generalising it into a rule.

## Safety And Scope

Encourage prompts to include:

- explicit scope limits
- definition of done
- exclusions
- no-fabrication rules where accuracy matters
- output structure that can be checked quickly

## Company / Product Guidance

Customize this section for your own context. Add your product terminology, internal roles, object names, workflows, and APIs so the skill produces prompts that fit your reality rather than generic ones.

Example entries:
- "Our product is called [X]. Key objects are [Y] and [Z]."
- "Default audience is [role]. Tone should be [description]."
- "Flag any assumptions about internal systems outside the prompt block."

## Prompt-Drafting Checklist

Use this mentally unless the user explicitly asks to see it:

- role or persona only when it adds value
- scenario or background
- explicit user goal
- inputs and their source
- output requirements
- examples (default on for format-sensitive or structured-tier outputs)
- XML structure (default on for structured-tier and above)
- validation instructions only where there is something concrete to check against — never reasoning scaffolding
- stop conditions and exclusions
- executor class, and effort level where the target exposes one
- destination input limit, if the prompt is going somewhere that truncates
- sub-agent spawn criteria and a delegation ceiling if orchestrator prompt

## Shortcut Triggers

Use this skill when the user says things like:

- `write me a prompt`
- `improve this prompt`
- `refine this prompt`
- `turn this into a better prompt`
- `design the prompt workflow`
- `build the agent prompt`
- `write me a handoff prompt`
- `write a fresh context brief`
- `write me a research prompt`
- `I want to kick this off`

## What Not To Do

- do not answer the prompt instead of refining it
- do not research the user's underlying topic unless they explicitly switch away from prompt-design mode
- do not overcomplicate simple asks with unnecessary prompt engineering jargon
- do not ask a long list of clarification questions when a clean first draft is good enough
- do not add chain-of-thought scaffolding — current models reason internally, and it competes with that
- do not write a frontier-model prompt as a step-by-step script; state the goal and the constraints instead
- do not hardcode model version names into a prompt or a skill unless the behaviour genuinely differs by version
