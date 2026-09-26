# Decisions

## Why this exists

Every piece in this collection passed through this skill on its way out,
so it ships too: the tool that cleans everything else, with its limits
stated as loudly as its features.

## Two jobs, kept separate

The skill states plainly that it **rewrites content** and is **not a
release-assurance gate**. The two jobs get conflated in practice: a clean
change summary reads as clearance. The fix wasn't to make the skill do
more, it was to make it say less about what it covers: "What this is NOT"
sits second in the file, ahead of the procedure, and "what not to do" ends
by refusing the exact misuse.

## Why two gates, not one

**The port is a code review, not a copy.** The first real release found
**ten defects** beyond sanitising, already present in the internal copy:
commands that couldn't work when pasted, claims true of one component
written as claims about the whole, numbers that had drifted between
documents. Sanitising found none of them, correctly: a name-and-path pass
doesn't test whether a command runs or a claim holds.

## Two practices worth stealing, neither part of the skill itself

- **A reviewer-only extraction audit per piece**: classify every source
  section as ported, adapted, or excluded, so review checks a mapping
  instead of re-deriving one.
- **A named inventory for a sensitive source**: list every class of
  sensitive item and grep the list against the output; any hit is a stop,
  not a judgement call.

## What stayed home

Very little; the source was close to public-shape already. A pointer to a
longer internal process became the self-contained "What this is NOT"
section. One trigger phrase naming a specific repo became generic. Em
dashes went.

## Open questions

- **Seven detection classes won't stay seven.** Industry-identifying
  worked examples and one-person quotes are the known gaps.
- **Placeholder style is a taste.** `[Your Company Name]` reads clearly
  but litters a document; some prefer fictional consistent names. Visible
  placeholders were chosen because they can't be mistaken for real
  content, which is also their cost.
- **Whether "do not over-sanitize" survives contact with fear.** The rule
  is real, but a nervous operator on a deadline will always strip too
  much. An enforceable version of "keep the useful stuff" would be an
  improvement.
