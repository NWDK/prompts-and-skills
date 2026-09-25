---
name: sanitize-for-sharing
description: >
  Prepare an internal skill, prompt, or markdown document for public
  sharing: strip internal references (company and product names, people,
  private paths, internal URLs, workspace-specific context) and replace
  them with generic placeholders, returning a change summary and the
  sanitized file for human review. A content-rewriting pass only, not a
  release-assurance gate. Use when preparing any internal document for a
  public or shared repository, as the first step of a longer release path.
---

# Sanitize for Sharing

## What this does

Takes an internal document (a skill, a prompt, a process, any markdown)
and returns it with the private context removed: names and paths replaced
with placeholders or plain-language descriptions, people removed,
workspace-specific sections swapped for a standard placeholder block, and
a change summary a human can review before anything ships.

Never publishes, pushes, or moves files, and never modifies the original.

## What this is NOT

**This rewrites content. It is not a release-assurance gate.** It looks at
the words in one file. A real release audit covers what this skill never
touches: git history, hidden and ignored files, embedded metadata,
credential patterns, code's network behaviour, licences and adapted
material, privately-resolving links, and whether the genericised thing
still works.

Both passes run on the exact files that will ship; passing this one
satisfies none of the other. The second pass is
[`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md).

[`example/`](example/) shows the gap: a planted credential survives
sanitisation untouched, because it carries no name this skill recognises.

## Core rule

Only produce the sanitized output and a change summary. Do not modify the
original file. Do not push, share, commit, or move anything.

## Input

A file path to the document to sanitize, or the content pasted directly
into the conversation. If a path is given, read the file first. If
neither is given, ask before doing anything else.

## Detection pass

Before rewriting, scan for and flag every instance of:

1. **Company and product names**: organisations, products, branded terms.
2. **Internal file paths**: `rules/x.md`, or an area folder like
   `work - company/context/`.
3. **Email addresses**.
4. **Person names**: a first name alone counts if it clearly means one
   person.
5. **Internal tool and system names**: internal codebases, platforms, or
   workflows by their in-house name.
6. **Internal URLs**: non-public or private-resource links.
7. **Workspace-specific sections**: content that only makes sense inside
   the originating workspace.

Do not flag public tools (GitHub, Figma, Slack, Notion, Linear), public
model names (Claude, GPT, Gemini), standard technical terms, or generic
role titles.

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

Return, in order:

1. **Change summary.** What was replaced or removed, grouped by type.
   Flag anything that needed a judgement call.
2. **Sanitized file.** The full sanitized content in a code block.

Add one closing line naming anything that still needs manual review.

## What not to do

- Do not over-sanitize: public tool names, model names, and standard
  technical terms stay; a document stripped of every noun stops being
  useful.
- Do not remove content genuinely useful to any reader, only what is
  specific to the original author's private context.
- Do not ask clarifying questions when the file is readable and the
  replacements are clear; flag uncertainties in the summary instead.
- Do not let a clean pass stand in for permission to publish; that
  decision belongs to the release audit and a human.

## Triggers

Use this skill when someone says things like:

- "sanitize this skill"
- "prep this for sharing"
- "clean this for the repo"
- "strip the internal stuff"
- "make this public-safe"
- "ready to push to the public repo"
