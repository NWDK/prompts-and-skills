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

## Default Behavior

1. For quick-tier requests, produce an improved prompt directly with minimal or no clarification.
2. For structured-tier and above, ask only the minimum questions needed to pin down: goal, inputs, audience, output format, constraints, model available, stakes.
3. If the user already pasted something that looks like a prompt, do not answer it. Refine it.
4. Default to one strong primary prompt. Add variants only when they materially help.

## Prompt Design Pattern

Use this pattern internally when drafting. Wrap sections in XML tags for any structured-tier prompt or above — Claude is trained on this structure and responds measurably better to it than plain paragraphs.

```
<role>...</role>
<task>...</task>
<context>...</context>
<examples>...</examples>          <!-- include for format-sensitive or accuracy-critical outputs -->
<reasoning>...</reasoning>        <!-- omit if model uses extended thinking -->
<output_format>...</output_format>
<stop_conditions>...</stop_conditions>
```

Quick-tier prompts do not need XML tags.

## Extended Thinking

For Claude models that support extended thinking (Sonnet 4.6, Opus 4.7):

- Do not add "think step by step" or manual chain-of-thought scaffolding. The model reasons internally and extra scaffolding can hurt performance.
- Omit the `<reasoning>` block. Prompt for outcomes, not steps.
- For agentic prompts, let the model think between tool calls rather than scripting the sequence.
- Extended thinking adds latency — recommend it only when multi-step reasoning will materially improve quality (research, complex analysis, agentic decisions).

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
- Recommend extended thinking if the target model supports it
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

If your workspace has multi-agent conventions, reference them here rather than re-documenting them in the prompt itself.

## Output Rules

1. Wrap each final prompt in triple backticks.
2. Keep commentary outside the prompt block.
3. Keep prompt-design notes concise and focused on decisions that materially change behaviour.
4. After delivering a prompt, invite iteration with a short follow-up.
5. Keep system prompts and agent prompts under 8000 characters unless the user explicitly wants longer.

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
- reasoning or validation instructions (omit if using extended thinking)
- stop conditions and exclusions
- model or config hints only when genuinely useful (including whether extended thinking applies)
- sub-agent spawn criteria if orchestrator prompt

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
- do not add chain-of-thought scaffolding for models that support extended thinking
