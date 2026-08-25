# Decisions

## Why this exists

Everything else I publish here assumes a working relationship with an AI
assistant that behaves like a colleague: says what it doesn't know, pushes
back, asks before building. Nothing else establishes that relationship; it
all stands on it. This is the piece that establishes it, and it is the set
of standing rules my own sessions actually load, rewritten for a reader who
is not me.

## A rewrite, not a bundle

The source material is the collaboration rules file my workspace auto-loads
into every session, plus a handful of workspace-level rules that earned
their place through repeated failures. Internally, those are numbered laws
in a filing system: terse, cross-referenced, reasons stored elsewhere or
nowhere, because their reader is an AI that only needs the law.

Publishing that shape would have been easy and wrong. A stranger cannot ask
what rule 17 meant, why it exists, or which rules matter most, and a bundle
of internal rule numbers is a workspace dump wearing a trench coat. So this
is a rewrite with two structural changes: the clauses are reorganised around
the relationship (truth, pushback, questions, communication, voice,
proportion, style) instead of around my filing system, and every clause in
the annotated version carries its why inline, because you will only enforce
a clause whose point you can feel, and an unenforced agreement decays into
decoration.

## What was selected from the wider rule set, and the test used

Beyond the collaboration file itself, the workspace has dozens of rules.
The selection test for this piece: **does the rule govern the human-AI
relationship itself, or does it govern a specific craft?** Relationship
rules came in; craft rules stayed home.

Selected in:

- **Never guess a retrievable value.** The retrieval-specific form of
  "never invent", and the failure I have been burned by most often: a
  guessed URL, ID, or figure reads exactly like a real one.
- **An absence is a claim.** "It isn't there" off one failed search is how
  confident wrongness most often enters a working session, because a wrong
  search and a true absence look identical from inside.
- **Never fabricate lived experience.** The highest-consequence special
  case: writing in someone's voice. It got its own section rather than a
  line, because the failure is self-concealing (invented experience reads
  better than truth) and the fix is checkable (every claim traces to
  something the person actually said).
- **A clean parse is not correctness.** One line in the truth section:
  well-formatted and wrong survives every surface check.
- **Match effort to stakes.** Performed rigour is a real failure mode, and
  an agreement that only adds obligations teaches the assistant to perform;
  this clause is the counterweight.

## What was deliberately left out

A rewrite must not become a land grab. These were left out even where the
seam was tempting, because each is a craft in its own right rather than a
property of the relationship:

- **Evidence discipline**: single observations are not rules, provisional
  claims stay labelled, research numbers earn their wiring. The agreement's
  truth clauses stop at "don't invent and don't overstate"; how to weigh
  accumulating evidence is a separate skill.
- **Multi-agent and delegation conventions.** The agreement governs one
  relationship, not a fleet.
- **How to brief an agent well.** The agreement obliges the assistant to
  ask; writing briefs that need fewer questions is the human's half of the
  same problem, and a different document.

The rule I applied: one idea lives in one place. Two copies of the same rule
drift apart, and the reader inherits the argument.

## The two versions

Beginners follow examples, not instructions, and nobody's first act is
reading an annotated agreement. So the short version is the actual product
for the reader this piece is aimed at: twelve numbered lines, one paste, a
style slot to personalise. The annotated version exists for the second
week, when a clause gets violated and you need its reasons to decide
whether to enforce or delete it. Compression choices: the source's five
sections and twenty-odd rules became twelve lines by folding (question
discipline into one line, communication rules into one line) and by
promoting the two sneaky truth failures (guessed retrievables, asserted
absences) to their own lines, because they are the ones a beginner will not
anticipate.

My own style preferences appear only as examples in the customise slot
(spelling register, punctuation bans, explain-terms-as-you-go). They are
real entries from my own agreement, but they are mine; shipping them as
defaults would confuse a personal preference with a principle.

## Why the never-invent clauses are not condensed

A pre-release audit recommended reducing the repeated forms of "never
invent" where one clause could cover them. Four of the twelve are members of
that family: clause 1 (don't invent), clause 4 (don't guess a look-up-able
value), clause 5 (an absence is a claim), clause 11 (don't invent my
experience). One clause could technically cover all four, and the block
would read tidier.

Kept separate deliberately, because they are four different failure modes
and only the first one feels like inventing at the time. Guessing a
plausible URL feels like reconstructing. Saying "it isn't there" after one
failed search feels like reporting. Writing a flattering line about someone
feels like writing. A single "never invent information" clause is agreed
with sincerely and then violated three ways before lunch, because the
assistant does not classify any of those three as inventing.

The specificity is the enforcement mechanism. You cannot point at the clause
that broke if the clause is general enough to cover everything. So the
compression went into the wording rather than the count: the block lost 135
characters and kept all twelve lines.

This is a live disagreement with a reasonable reviewer, not a settled fact.
If you condense them and the agreement holds, I want to know.

## Sizing, and why the block is not duplicated in the README

The block is sized to fit small standing-instruction fields, because the
reader most likely to need this piece is the one on a free tier with a
capped box. Per-host caps are not printed anywhere in the piece: they differ
by host and by plan, they have already moved once during this piece's life,
and a number that is wrong reads as authoritative in a way that a missing
number does not. What is printed is the measured size of our own file, which
cannot date, plus the order to cut in.

The README links to the block rather than reproducing it. One extra click
against two copies drifting apart, which is the failure this piece warns
about in the section above.

## The claim I removed

An earlier draft of the README promised what you'd notice in the first
session: more "I don't know", more questions before drafts, at least one
plan getting pushed on. All three happen to me. I cut them anyway.

Every account I own already runs these rules, which means I've never
actually used a naive assistant to test the path this README tells you to
take. Paste it cold, nothing else supporting it, one settings box. The
rules working inside my setup and the rules working as pasted text are two
claims, and only the first one has anything behind it.

So the README now says what I know instead of what I hope. If you run it
cold and it does nothing, that's the finding I'm missing, and I'd rather
have it in an issue than keep promising it.

## What I'd want pushed back on

- **Is twelve too many?** Standing-instruction space is contested in some
  tools, and every line dilutes the others. If you would cut to eight, I
  want to know which four died.
- **The enforcement claim is folk practice.** "Point at the clause when it
  breaks" matches my experience and I have not measured it. If you find the
  agreement holds without enforcement, or decays even with it, that is
  data I do not have.
- **How much of the improvement is the model changing versus me noticing?**
  The truth clauses make violations legible, which changes my behaviour as
  well as the assistant's. I think both effects are real and I cannot
  cleanly separate them from inside my own sessions.
