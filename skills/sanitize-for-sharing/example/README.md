# Worked example

`before.md` is a synthetic skill file with problems planted on purpose.
`after.md` is what this skill produces.

What it left alone and missed matters as much as what it caught.

## Caught

| Planted | Became |
|---|---|
| Company `Harbourline` | `[Your Company Name]` |
| Product `Dockside` | `[Your Product Name]` |
| People `Priya`, `Marcus` | "a reviewer", "a backup reviewer" |
| Two emails | "your incident address", "a shared inbox" |
| Tool `Beacon` | "an internal dashboard" |
| URLs on `harbourline.internal` | a `.example` host |
| Two workspace-path shapes | plain-language descriptions |
| A whole context section | the placeholder block |

## Left alone, correctly

GitHub stayed, three times, since genericising it would weaken the
instructions. So did "the designer" and the `.example` domains.
Over-sanitising makes a file too vague to use.

## Missed, on purpose

Line 37 of `before.md` carries a credential:

```
export TOKEN=glpat_7bQx2mKd91LtVnR4sYeW
```

It survives into `after.md` unchanged. The token above it was caught only
for carrying the company name, `$HARBOURLINE_API_KEY`. This one has no
company marker to catch.

This skill reads for context, not secrets: a nameless credential is
invisible to it. A separate entropy scan over the staged files still has
to happen.

## What the rules cost

Replacing a whole section takes reusable parts with it. The planted
section named Figma and a `package.json` script, both normally kept, and
both went with the section.
