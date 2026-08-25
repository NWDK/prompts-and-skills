# Worked example

`before.md` is a synthetic skill file for a company that does not exist,
with problems planted in it deliberately. `after.md` is what this skill
produces. Nothing here came from a real workspace.

Read the two side by side. The interesting parts are what it left alone and
what it missed.

## Planted, and caught

| Planted | Became |
|---|---|
| Company name `Harbourline` | `[Your Company Name]` |
| Product name `Dockside` | `[Your Product Name]` |
| Two people, `Priya` and `Marcus` | "a reviewer" and "a backup reviewer" |
| Two emails | "your incident address", "a monitored shared inbox" |
| Internal tool `Beacon` | "an internal dashboard, if you have one" |
| Internal URLs on `harbourline.internal` | a generic `.example` host |
| Workspace path `work - harbourline/context/product-glossary.md` | "your product glossary" |
| Workspace path `rules/customer-comms-rules.md` | "your customer-communications guidelines" |
| A whole company-context section | the standard placeholder block |

## Planted, and correctly left alone

The near-misses matter as much as the hits. Over-sanitising produces a file
too vague to use, which is its own kind of broken.

GitHub stayed, three times. It's a public tool and genericising it would
have made the instructions worse. So did "the designer", a generic role
rather than a person, and the `.example` domains, which exist precisely to
be safe in documentation.

## Planted, and missed, on purpose

Line 37 of `before.md` carries a credential:

```
export TOKEN=glpat_7bQx2mKd91LtVnR4sYeW
```

It is still there in `after.md`, unchanged.

That is the demonstration. The token one line above it was caught, but only
because it was called `$HARBOURLINE_API_KEY` and the company name was in
it. This one has no company marker, so nothing about it looks like the
thing the skill is scanning for. It reads as ordinary text and passes
straight through.

This skill reads for private *context*. It does not scan for secrets, and a
credential without a recognisable name attached is invisible to it. That is
why the SKILL says a content rewrite is not a release gate, and why an
entropy scan over the exact staged file set is a separate job that still
has to happen.

## One thing the rules cost

Replacing a whole section is blunter than replacing terms inline, and it
takes the reusable parts with it. The planted context section mentioned
Figma and a `package.json` build script, both of which the detection rules
say to leave alone. They went anyway, because they sat inside a section
that got replaced wholesale.

The output ends with a couple of generic sentences putting that guidance
back. Worth knowing that you may have to, because the section rule cannot
see what it is taking.
