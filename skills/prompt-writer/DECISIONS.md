# Decisions: prompt-writer

What this is, where it came from, and the calls made along the way, including the one that was already wrong by the time I noticed it.

## Origin

I wrote this because I was writing the same prompt badly in four different shapes. A prompt for a model I am talking to interactively is not the same artefact as a prompt for a one-shot run, or for a sub-agent that cannot ask me anything, and I kept discovering that only after the output came back wrong.

## Decisions

### Executor class, never model versions

The single most important rule in this skill: it reasons about **executor class** (frontier interactive, one-shot, sub-agent, external) and never about named model versions.

That was not a design instinct. It was forced. I refreshed the internal copy in **July 2026** and it was **already wrong by August**: it named a specific small model as supporting adaptive thinking, which that model does not do. One month of shelf life on a hardcoded capability claim.

So a version number in a prompt-design skill is a maintenance commitment you will not keep, and worse, it fails silently. Nobody gets an error. The prompt just quietly stops matching the thing it is aimed at. Executor class is stable because it describes the **situation** (can this thing ask me a question? does it get one shot?) rather than the vendor's current lineup.

### The Executor axis is orthogonal to complexity, not a second version of it

Complexity tiers already existed. The instinct was to fold executor into them, treating "sub-agent" as a complexity level. That is wrong: a trivial task for a sub-agent still needs the full self-contained treatment, because the sub-agent cannot ask. They are two independent axes and collapsing them loses the case that actually bites.

### Reasoning and Effort replaced Extended Thinking

Terminology drift, tracked down and removed in full: six stale references, including a whole worked block built around the old model. Half-renaming a concept is worse than not renaming it, because the reader cannot tell which half is current.

### The arbitrary character cap was deleted, not adjusted

An earlier version capped prompts at 8000 characters. That number had no source. It was not measured against anything, and a reader would reasonably assume it was.

It was replaced by two things that are actually checkable: **signal density** (is every line earning its place) and **a check against the destination's real input limit**, which is a fact you can look up for your own tool rather than a number I made up.

### A limit true of one surface stayed out of the public copy

I measured a hard input limit on one specific command in one specific tool: 4000 characters, rejected outright with an error rather than truncated. That is a genuinely useful, hard-won fact.

It is **deliberately not in the public skill.** It is true of one surface, and published here it would read as a general rule about prompt length. The public copy carries the general form instead: find your destination's limit, and find out whether it truncates or refuses, because those fail very differently. Truncation is the dangerous one, since it succeeds.

That distinction is the whole discipline of this repo in one decision: a true statement about one component, written as a statement about everything, is how a document becomes false without anyone editing it.

### The sub-agent section grew because two failure modes kept recurring

Both are counterintuitive:

1. **A sub-agent starts blind, and usually cannot ask.** Everything it needs must be in the prompt. Not "in the project", not "obvious from context". In the prompt. This was written as an absolute and later scoped: some harnesses can message a running sub-agent, so "cannot ask" is a property of the harness rather than of sub-agents. The guidance is unchanged, because none of them make it easy and assuming you get one turn is the safe way to be wrong.
2. **Current models over-delegate.** The useful guidance is a **ceiling**, not encouragement. Left alone, they will fan work out past the point where coordinating it costs more than doing it.

The second one is the reason this section exists at all. Every other piece of writing on the subject assumes you need persuading to delegate more.

### The framing was the dated part, not the advice

An audit called this piece out for being generic and time-sensitive. Reading
it again, the advice inside was mostly current: don't script a frontier
model, don't add chain-of-thought scaffolding, effort is the dial rather
than thinking. What was dated was the *opening*, which sold the skill on
turning a messy request into a structured prompt. That was the 2023 problem
and it has largely stopped being one.

So the reframe leads with the case against using it. Most prompt
engineering has stopped paying, and if you can see the output and correct
it, that beats any prompt this writes. What survives is the case where
correcting is not available: a handoff to a fresh context, a sub-agent
brief, an unattended run, deep research. Four cases, all of them the same
shape, which is that the prompt has to carry everything because there is no
second turn.

A prompt skill that opens by telling you when not to use a prompt is a
better argument for its own judgement than any list of techniques.

### The XML claim was folklore

It said Claude "responds measurably better" to XML-tagged sections than to
plain paragraphs. No source, and stated as a blanket performance fact.
Tags earn their place when a prompt is long enough that a section needs
referring to later, or when something other than a person parses it. That
is a real reason and it survives a model release. Tagging a three-line
request is cargo cult.

## Known limits, and why they are near the top

The repo README tells a reader that every skill states its limits near the top, and that a missing one is an oversight rather than a decision. That was a promise the collection was not keeping. This skill now carries five.

## Rejected

- **Naming models.** See above. Rejected permanently, not pending a better list.
- **A single blended complexity-and-executor scale.** Loses the trivial-task-for-a-blind-agent case, which is the common one.
