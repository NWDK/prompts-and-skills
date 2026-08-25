---
name: sanitize-for-sharing
description: >
  Prepare an internal skill, prompt, or markdown document for public sharing
  by stripping internal references (company and product names, people,
  private paths, internal URLs, workspace-specific context) and replacing
  them with generic placeholders, then returning a change summary and the
  sanitized file for human review. This is a content-rewriting pass only: it
  is NOT a release-assurance gate, and running it does not make anything
  safe to publish on its own. Use when preparing any internal document for
  a public or shared repository, as the first step of a longer release
  path.
---

# Sanitize for Sharing

## What this does

Takes an internal document (a skill, a prompt, a process, any markdown)
and returns a version with the private context removed: company and
product names replaced with placeholders, internal paths replaced with
plain-language descriptions, people's names and addresses removed, and
workspace-specific sections swapped for a standard "customise this" block.
It also returns a change summary, so a human can review what moved before
anything ships.

It does not publish, push, or move files, and it never modifies the
original. It produces a candidate for review. A human does the publishing.

## What this is NOT, and what must still happen

Read this section before trusting the output with anything.

**This skill rewrites content. It is not a release-assurance gate, and it
cannot be turned into one by running it carefully.** It looks at the words
in one file. A real release audit looks at everything else, none of which
this skill touches:

- git history (the deleted secret is still in the history);
- hidden files, symlinks, and ignored-but-present files in the staged set;
- embedded metadata in images and documents;
- high-entropy strings and credential patterns, scanned mechanically, not
  read for;
- what any included code actually does on the network;
- licences, and material adapted from other people's work;
- links that resolve privately for you and break or leak for everyone
  else;
- whether the genericised thing still works at all, which only a test or a
  stranger following the README can tell you.

Both passes have to happen, on the **exact set of files that will ship**,
and passing this one satisfies none of the other. The second pass is
[`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md), beside this file.

[`example/`](example/) shows the gap concretely: a planted credential
survives sanitisation untouched, because it carries no name the skill has
any reason to recognise. The first time I put a
real tool through a full release path, the process beyond sanitisation
found ten defects that already existed in the internal copy. Sanitising
had, correctly, found none of them: they were not sanitisation problems.
Treat this skill as step one, and budget for the rest.

## Core rule

Only produce the sanitized output and a change summary. Do not modify the
original file. Do not push, share, commit, or move anything.

## Input

One of:

- a file path to the document to sanitize;
- the content pasted directly into the conversation.

If a file path is given, read the file first. If neither is provided, ask
for it before doing anything else.

## Detection pass

Before rewriting, scan for and flag every instance of:

1. **Company and product names**: organisation names, product names,
   branded terminology.
2. **Internal file paths**: workspace-relative paths (the shape
   `rules/something.md`, or an area folder like `work - company/context/`).
3. **Email addresses**: anything matching an email pattern.
4. **Person names**: named individuals. A first name alone counts when it
   clearly refers to a specific person.
5. **Internal tool and system names**: internal codebases, platforms, or
   workflows referenced by their in-house name.
6. **Internal URLs**: non-public links, or links to private resources.
7. **Workspace-specific sections**: whole sections whose content only
   makes sense inside the originating workspace.

Do not flag: well-known public tools (GitHub, Figma, Slack, Notion,
Linear), public model names (Claude, GPT, Gemini), standard technical
terms, or generic role titles (designer, engineer, marketer).

## Replacement rules

Apply in order. When in doubt, replace rather than keep.

| What | Replace with |
|---|---|
| Company name (inline) | `[Your Company Name]` |
| Product name (inline) | `[Your Product Name]` |
| Person name | Remove, or `[Team Member]` if the reference must stay |
| Email address | `[your@email.com]` |
| Internal file path | A plain-language description of what the resource is (for example, "your workspace's multi-agent conventions") |
| Internal URL | Remove |
| Entire workspace-specific section | The standard placeholder block below, keeping the section heading |

## Standard placeholder block

When an entire section is workspace-specific, replace its body with:

```text
Customize this section for your own context. Add:
- Your product or company name and what it does
- Key objects, roles, or terminology your team uses
- Internal workflows or conventions the skill should be aware of
- Any APIs, tools, or systems the skill should reference by name

Example entries:
- "Our product is called [X]. Key objects are [Y] and [Z]."
- "Default audience is [role]. Tone should be [description]."
- "Flag any assumptions about internal systems outside the prompt block."
```

## Output format

Return two things, in this order:

**1. Change summary.** A short bulleted list of what was replaced or
removed, grouped by type. Flag anything that needed a judgement call:
ambiguous proper nouns, content that could go either way. Keep it
scannable; it exists for a quick human review before the next gate.

**2. Sanitized file.** The full sanitized content in a code block, ready
to copy onward.

After both, add one line naming anything that still needs manual review.

## What not to do

- Do not modify the original workspace file.
- Do not push, share, commit, or move anything.
- Do not over-sanitize: generic technical terms, public tool names, and
  public model names do not need replacing, and a document stripped of all
  its nouns stops being useful to anyone.
- Do not remove structural or instructional content that is genuinely
  useful to any reader; only remove what is specific to the original
  author's private context.
- Do not ask clarifying questions when the file is readable and the
  replacements are clear; do the pass and flag uncertainties in the change
  summary.
- Do not let anyone, including yourself, treat a clean pass from this
  skill as permission to publish. That decision belongs to the release
  audit and a human.

## Triggers

Use this skill when someone says things like:

- "sanitize this skill"
- "prep this for sharing"
- "clean this for the repo"
- "strip the internal stuff"
- "make this public-safe"
- "ready to push to the public repo"
