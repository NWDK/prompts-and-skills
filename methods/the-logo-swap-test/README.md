# The Logo Swap Test

One question for whether an interface contains any decisions:

> Could a competitor swap in their logo and keep the design?

If yes, nothing on the screen belongs to the product. That's the actual
problem, and it's worth separating from the question people usually ask
instead.

## "Is this AI-generated" is the wrong question

Most writing on this is a banned-motif list. Purple gradients, glass cards,
that one font, rounded everything. Lists like that are wrong in both
directions: they punish genres that legitimately own those features, and
they miss a generic interface built entirely from unfashionable parts.

Whether a machine made it doesn't matter. Plenty of hand-built interfaces
fail the logo swap, and a machine-built one that made real decisions passes.
What you're looking for is unexamined defaults, whatever produced them.

## One feature is never the finding

The single most common mistake is converting a surface feature straight into
a verdict. A gradient is an ingredient. So is a font, a radius, an icon set.

Give every observation exactly one label:

- **Surface feature.** A neutral ingredient. Not evidence of anything on its
  own.
- **Repeated default.** One treatment imposed across unrelated content,
  ignoring hierarchy and how sensitive the material is.
- **Family-style cluster.** Several correlated defaults appearing together
  across major regions.
- **Poor craft.** A hierarchy, state, responsive or accessibility failure.
  Different from looking generic, and often more urgent.
- **Low brand specificity.** The logo swap. Different again from poor craft:
  an interface can be beautifully made and belong to nobody.

A finding gets real when several hold at once: correlated defaults appearing
together, repeating across regions, applied to content of clearly different
importance, with no relationship to the task or audience, and no authentic
product states or proprietary material anywhere.

"Three correlated features across two major regions" is a useful prompt to
go and look harder. It is not a threshold and I have not validated it as one.

## Look before you measure

Before reading the source, the prompt, or who made it, look at the render
and write down four things: the dominant motifs, any family resemblance you
suspect, the single most distinctive element, and what would survive the
logo swap.

Do this first or you don't get to do it at all. Once you know the interface
came out of a model, you will find model tells, and you won't be able to
tell that from seeing them. If you already know, say so in the report and
still record the impression before opening anything.

## Test every finding against the genre

This is the step that separates an audit from a banned list. A naive
detector punishes precisely the features some genres own.

| Genre | What a naive detector flags | The better question |
|---|---|---|
| Editorial | Serif, mono metadata, paper tones, rules | Does hierarchy respond to the material, or is editorial chrome pasted on? |
| Brutalist | Raw HTML, hard borders, default link blue | Is the constraint coherent and functional, or just broken? |
| Luxury | Sparse copy, centred, oversized serif, neutral | Is there proprietary art direction and material detail? |
| Developer tool | Dark theme, mono, grids, outline icons | Are the data, states and density authentic to the workflow? |
| Documentation | Repetition, cards, accordions, side nav | Is the repetition the content's own taxonomy? |
| Design system | Default tokens, radii, icon specimens | Is this the system's own authored language? Compliance proves consistency, never quality |

A design-system specimen page should be excluded from provenance findings
entirely. It is supposed to look like its own defaults.

## Don't score it

I built a numeric version first and killed it. A score out of twenty
launders a judgement call into something that looks measured, and the number
gets quoted downstream long after the reasoning is gone.

Four verdicts, all categorical. **Clean**, **Watch**, **Slop risk**, and
**Unscored** for when you couldn't see enough to say. Anyone selling you a
numeric slop detector is selling false precision.

## You are the worst judge of your own accent

If you are using a model to run this, it under-rates its own family's house
style. It hears its own accent as no accent.

I have watched this twice, in both directions. A Claude grader scored a
Claude-built guide as fully authored. A GPT grader scored its own family's
redesign clean. Both were corrected only by a different model family plus a
person. Two cases is not a law and I'm not claiming one.

So when the thing you're auditing plausibly matches the house style of the
model auditing it: say so, drop your confidence, and mark any Clean verdict
provisional. Mechanical evidence and craft findings are still fine, judge
those normally.

A single-model audit that declares its blind spot is a valid result. One
that quietly returns Clean on its own family's work is not.

## What it won't tell you

Whether the design is good. This finds unexamined defaults and missing
decisions. An interface can pass the logo swap, be full of authored
decisions, and still be worse than the generic version it replaced.

## Feedback

If a genre control misfires or you find a class this misses:
[open an issue](../../issues).
