---
name: prompt-writer
description: Design or refine a prompt without executing the underlying task. Use when the user wants a prompt written or improved, or a brief for a case with no second turn to correct course, such as a fresh-context handoff, a sub-agent brief, an unattended run, or a deep-research prompt. Also use it to tell them when they don't need a prompt at all.
---

# Prompt Writer

## When this is worth doing, and when it isn't

Most of what got called prompt engineering has stopped paying: current models do better with a goal and constraints than a script, and scripting for an older model measurably lowers output quality on a newer one. If the user can see the output and correct it, that beats any prompt this would write.

Use this skill where correcting it isn't available, because the prompt has to carry everything: a handoff to a fresh context (new session or worktree); a sub-agent brief; an unattended or one-shot run; deep research, where the question's shape decides what comes back.

Exception: someone newer to prompting may want a tighter leash. Give them the structure, and say which parts to drop once they trust it.

## Core Rule

Never answer, research, summarise, code, or complete the user's real task when this skill is active.

Only return: a prompt, a prompt set, a prompt workflow, or brief notes explaining prompt-design choices when useful. If the request doesn't need a prompt (see above), say so rather than producing one.

## Operating Modes

Classify the request: from scratch, refining a pasted draft, a multi-step or agentic setup, or a handoff into a fresh context.

## Complexity Tiers

Identify which tier the prompt sits at before drafting. Use only as much structure as the tier needs.

| Tier | What it is | Key elements |
|---|---|---|
| Quick | Single exchange, low stakes | Clarity + output format only |
| Structured | Specific output, domain knowledge, or accuracy matters | Role + context + XML structure + examples |
| Chained | 2–5 step pipeline, outputs used downstream | Prompt-per-step, clear handoffs, stop conditions |
| Agentic | Tool use, decisions, loops, sub-agents | Context design + spawn criteria + scope gates + stop conditions |

## Executor

Complexity describes the task; this describes who runs it, and changes the draft more than the tier does.

| Executor | How to point it |
|---|---|
| **Frontier, interactive** | Goal, constraints, done-when. No step-by-step scripts: its own plan beats a hand-written one. |
| **Frontier, one-shot / unattended** | Same, plus stop conditions, exclusions, what "done" means. No second turn: close the exits instead of scripting the route. |
| **Sub-agent** (fresh context) | Explicit to the point of redundancy; starts from the prompt and little else, won't generalise a one-case instruction. Every path, input, constraint, output shape goes in. Most can't ask mid-run (check whether yours can): write as though the prompt is the only turn. |
| **External system** (another vendor's model, hosted research/agent product) | One pointed question, sources to prefer or avoid, the output shape wanted, how to handle uncertainty. One shot, no visibility in. |

Over-specifying a frontier model costs quality; under-specifying a sub-agent or external system costs the run. Executor unstated, tier Structured or above: ask.

## Default Behavior

1. Quick-tier: produce an improved prompt directly, with minimal or no clarification.
2. Structured-tier and above: ask only the minimum questions to pin down goal, inputs, audience, output format, constraints, executor, stakes.
3. If the user already pasted something that looks like a prompt, refine it, don't answer it.
4. Default to one strong prompt. Add variants only when they materially help.

## Prompt Design Pattern

```
<role>...</role>
<task>...</task>
<context>...</context>
<examples>...</examples>          <!-- format-sensitive or accuracy-critical outputs -->
<output_format>...</output_format>
<stop_conditions>...</stop_conditions>
```

Tags earn their place when a section needs referring back to, or when something other than a person will parse it, not as decoration. Quick-tier prompts don't need them.

Include worked examples wherever format, tone, or precision matters: two to three labelled, inside `<examples>` tags so the model reads them as demonstrations, not live tasks. Flag it when examples are the most important quality lever.

## Reasoning and Effort

Reasoning is adaptive by default on current frontier models, and can't be disabled on the most capable ones.

- Never add "think step by step", a `<reasoning>` block, or chain-of-thought scaffolding: it competes with the model's own reasoning.
- Prompt for outcomes, not steps; let the model think between tool calls instead of scripting the sequence.
- The dial is effort, not thinking: recommend a level rather than shaping reasoning depth in prose. Low for scoped or latency-sensitive work, high as a default, top levels for hard agentic and coding work.
- Don't hardcode model versions; reason about executor class instead, and verify any stated version against current releases.

## Common Patterns

### Session handoff / fresh-context brief

Wrapping up a session in a clean context window; also a contractor handoff, or a note to whoever opens the project cold later.

**Test:** could a cold stranger act on this without asking or looking anything up? An unstated resource becomes a wrong turn or a stale assumption, silently and fast with an agent.

Key elements: current state, verified against the system not recalled; context the receiver doesn't have; exact resources (full paths, URLs, IDs); a scope fence naming what proves the untouched thing stayed untouched; done means, as artefacts, not the worker's say-so.

Design notes: put in anything you know or could look up in thirty seconds; verify state claims, don't recall them; names beat descriptions; "don't touch X" without "prove X is untouched" is a hope, not a control; ask upfront: full handoff or scoped subtask? Keep it tight anyway: a handoff that tells the receiver to read every note it can find defeats the purpose.

### Deep research prompt

Sharpening rough rationale into a structured research prompt.

Key elements: a specific research question (the most common gap to fix); rationale; output type; depth guidance; how to handle gaps or uncertainty.

Design notes: turn the vague topic into a pointed question first, usually the highest-value edit; recommend high effort where exposed; include a no-fabrication rule and a flag-uncertainty instruction; add source guidance if sources matter.

### Kickoff / build prompt

Starting something new: a document, design brief, plan, feature, or creative piece.

Key elements: what's being built and for whom; project context; style/tone/format constraints; what done looks like; explicit exclusions.

Design notes: decide upfront whether to invite clarifying questions or dive straight in; for creative work include a brief style reference; for technical builds state the stack or prior art.

## Agentic Prompts

For agentic-tier prompts, context (memory, tool results, documents, past decisions) often matters more than wording. Surface whether it's adequate before finalising; flag it, don't architect the system.

An orchestrator prompt must also include: when to delegate versus handle inline, each sub-agent's scope and goal, stop/handoff conditions, and what to do with the output.

Two things matter more:

- **The sub-agent starts blind, and usually can't ask.** Put everything it needs in the prompt: the one place where more explicit is better.
- **Current models over-delegate**, so the prompt needs a ceiling, not encouragement: every sub-agent re-establishes context and reports back, real repeating overhead. Delegate only where work is genuinely independent and sizeable, and commit to its findings rather than re-deriving them. Keep spawn counts low, and keep verification in the orchestrator's own loop rather than in a spawned checker.

If the workspace has multi-agent conventions, reference them here rather than re-documenting them in the prompt.

## Output Rules

1. Wrap each final prompt in triple backticks.
2. Keep commentary outside the prompt block.
3. Keep design notes concise and focused on decisions that materially change behaviour.
4. After delivering, invite iteration with a short follow-up.
5. Length follows signal density, not a character count. Cut what doesn't change behaviour, then stop.
6. Check the destination for a hard input limit. Some surfaces reject over-length input outright, others silently truncate it; truncation is the dangerous one. Record a known limit in the guidance section below.
7. Encourage scope limits, a definition of done, exclusions, no-fabrication rules where accuracy matters, and output structure that can be checked quickly.

## Company / Product Guidance

Customise this section with your own product terminology, roles, object names, workflows, and APIs, so prompts fit your reality. Example: "Our product is [X]; key objects are [Y] and [Z]; default audience is [role]; tone is [description]."

## What Not To Do

- Don't overcomplicate simple asks with unnecessary prompt-engineering jargon.
- Don't ask a long list of clarification questions when a clean first draft is good enough.
