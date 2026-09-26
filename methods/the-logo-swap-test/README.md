# The Logo Swap Test

One question for whether an interface contains any decisions:

> Could a competitor swap in their logo and keep the design?

If yes, nothing on the screen belongs to the product.

## "Is this AI-generated" is the wrong question

Most writing on this is a banned-motif list: gradients, glass cards,
rounded everything, punishing genres that legitimately own those features
while missing a generic interface made from unfashionable parts. Whether
a machine made it doesn't matter: look for unexamined defaults.

## One feature is never the finding

The common mistake: converting a surface feature straight into a verdict.
One label per observation:

- **Surface feature.** Neutral, not evidence on its own.
- **Repeated default.** One treatment imposed across unrelated content.
- **Family-style cluster.** Correlated defaults across major regions.
- **Poor craft.** A hierarchy or accessibility failure, often more urgent
  than generic.
- **Low brand specificity.** The logo swap itself.

A finding gets real when several hold at once: correlated, repeating,
unrelated to task or audience.

## Look before you measure

Before reading the source or who made it: note the dominant motifs, any
family resemblance, the most distinctive element, and what would survive
the logo swap. Do this first, or not at all: once you know a model made
it, you'll find tells you can't un-know.

## Test every finding against the genre

This separates an audit from a banned list: a naive detector punishes the
features some genres own.

| Genre | Naive flag | Better question |
|---|---|---|
| Editorial | Serif, paper tones | Responds to material? |
| Brutalist | Raw HTML | Coherent, or broken? |
| Luxury | Sparse, centred serif | Proprietary art direction? |
| Dev tool | Dark theme, mono | Authentic states, density? |
| Design system | Tokens, specimens | System's own language? |

A specimen page is excluded entirely, meant to look like its own
defaults.

## Don't score it

I built a numeric version and killed it: a score launders a judgement
into something that looks measured, and outlives the reasoning. Four
categorical verdicts instead: **Clean**, **Watch**, **Slop risk**, and
**Unscored** for when you couldn't see enough to say.

## You are the worst judge of your own accent

A model running this under-rates its own family's house style: it hears
its own accent as no accent, and I've watched this twice, corrected only
by a different model family plus a person.

When the target plausibly matches the auditing model's own style: say so,
drop confidence, mark any Clean verdict provisional.

Escalate only when the decision matters, the verdict is disputed, or an
own-family design came back Clean; otherwise, naming the blind spot is
enough.

## What it won't tell you

Whether the design is good. This finds unexamined defaults, not quality.

## Feedback

If a genre control misfires or you find a class this misses:
[open an issue](../../issues).
