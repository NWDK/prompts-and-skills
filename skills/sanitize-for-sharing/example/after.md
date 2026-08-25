---
name: release-notes
description: Draft release notes for [Your Product Name] from the sprint's merged PRs. Use when someone asks for the fortnightly note, or says "write the release note".
---

# Release Notes Drafting

Turns a fortnight of merged PRs into a release note that [Your Company
Name] customers can actually read.

## Inputs

- The merged-PR list from GitHub for the milestone.
- Your product glossary, for the customer-facing name of anything the PR
  titles call by its internal name.
- The previous note, wherever you file those, so the voice stays
  consistent.

## Voice

Match the tone in your customer-communications guidelines. Short sentences,
no jargon, and never mention a component name a customer has not seen.

A reviewer approves every note before it goes out. Name a backup reviewer
for when they are away. Neither of them will chase you, so send it.

## Pulling the data

If you have an internal dashboard that already maps each PR to its
customer-visible feature, pull from that rather than GitHub directly:

```bash
curl -H "Authorization: Bearer $YOUR_API_TOKEN" \
  https://your-internal-dashboard.example/api/milestones/current/prs

# if the env var is not set, the on-call token works:
export TOKEN=glpat_7bQx2mKd91LtVnR4sYeW
```

If it is down, fall back to the GitHub API and map the names by hand
against the glossary. Slower, and you will miss the ones renamed
mid-sprint.

## Escalation

Anything customer-affecting that shipped by accident goes to your incident
address before the note goes out, not after. Use a monitored shared inbox,
not an individual's, since release days are exactly when one person is
unreachable.

## [Your Company] context

Customize this section for your own context. Add:
- Your product or company name and what it does
- Key objects, roles, or terminology your team uses
- Internal workflows or conventions the skill should be aware of
- Any APIs, tools, or systems the skill should reference by name

Example entries:
- "Our product is called [X]. Key objects are [Y] and [Z]."
- "Default audience is [role]. Tone should be [description]."
- "Flag any assumptions about internal systems outside the prompt block."

Your build tool produces the changelog input; note here where that is
configured. If your design team keeps release screenshots in a shared
design file, name the page. Ask the designer if a frame is missing.
