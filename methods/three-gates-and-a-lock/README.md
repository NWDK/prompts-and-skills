# Three Gates and a Lock

How to approve work you cannot personally re-derive.

I direct agents to build things I can't audit line by line. The one that
forced this was a design system: every component carrying properties,
bindings and variants that all have to be right, and more of them arriving
than I could check. Eyeballing doesn't scale, and it misses the failures
that matter most, which are the ones that look completely fine.

This is the shape that worked. It isn't specific to design, or to Figma. It
applies wherever something gets produced faster than you can check it.

## The problem it solves

A single "run the checklist, mark it done" pass has a structural weakness:
whatever made the change is also grading its own work, in the same context,
already believing it got things right.

That isn't a discipline problem you can fix by being more careful. The pass
that produced the artefact is blind in exactly the places it was blind
while producing it.

## Gate 1: semantic. Does it mean the right thing?

Intent, naming, content. Is this the right thing, described correctly, for
the case it claims to serve?

This gate is allowed to make changes, and it runs first for that reason.
Verifying intent frequently reworks the thing, and you want the rework to
happen before the passes that check the reworked version.

A structural check cannot do this job. It verifies wiring, never truth. I
learned that from the same failure three times: a swatch that looked right
and was unbound, a clean "zero findings" pass on something that rendered
broken, and a documentation box confidently describing a variant that had
been deleted.

## Gate 2: independent QA. Fresh eyes, and no pen

A second pass, in a session that did not produce the work, checking it
against everything that has to hold true.

Two constraints make this gate work, and dropping either one hollows it out.

**It runs separately.** A same-session self-check is the exact thing this
exists to prevent.

**It cannot write the approval.** QA reports, it never corrects and never
marks. A pass that knows it has to produce a tick has a stake in passing,
and its whole value comes from having no outcome to protect. Keeping one
writer also keeps one audit trail.

The clearance is tied to a specific version. Any change after this gate
reads the item voids it. There is no "still basically the same".

## Gate 3: mechanical. Does it actually do the thing?

The deterministic checks, and then the approval marker.

This runs last because it is the lock. It doesn't introduce changes: if it
finds something wrong it stops and reports rather than fixing it inline,
because fixing inline would mean the thing it is about to approve was never
verified. Before declaring done, it re-checks its own claims against live
state rather than trusting what earlier gates reported.

## The lock: approved means frozen

Once something carries the marker, nothing modifies it without an explicit
instruction naming that specific item.

This is the half people leave out, and without it the gates are decorative.
Work that was verified and correct can quietly stop being correct, because
something downstream edited it in good faith. Then the marker is a lie, and
every gate that produced it was wasted.

Three properties make the lock hold:

**It survives permissive modes.** Running an agent with expanded permissions
authorises tool use, not changes to approved work.

**Sub-agents inherit it.** Any prompt that could touch approved work has to
restate the rule, and a sub-agent that realises its task implies modifying
an approved item stops and escalates rather than deciding for itself.

**Authorisation is narrow.** It covers the named item, in the current
session, for the change described. Not related items, not a second edit,
not later sessions. If a second change is needed, ask again.

You will want to waive a gate sometimes, and that's fine. Record it as a
waiver, naming the item, so anyone downstream can see the thing shipped
unverified. A waiver recorded is a decision. A gate silently skipped is a
false clearance.

## What convinced me

I reordered these gates because the evidence was embarrassing.

Two independent QA runs over four components that were **already approved**
found defects in all four:

- One had been approved for a struck-through price that existed only as a
  hand-painted override on two demo screens. The component itself rendered
  the price unstruck. Every screenshot passed. Both review gates passed.
- One had a fix for one check that introduced a failure in another.
- One had no developer note at all, despite four properties and live wiring.
- One had its primary property dead on twelve of sixteen variants. Three
  live screens were rendering a quantity of twenty against a property set
  to one.

Four for four. The fourth had been deliberately held back for its own QA
pass, and that hold is the only reason anyone caught it, by which point it
was already live in three places.

The lesson wasn't that the checks were bad. The checks were fine. The
approval was being applied before the evidence was in, by the same pass
that generated the evidence.

## Cost, honestly

This doesn't add a step if you were already doing QA. It reorders the steps
you have and moves the approval to the end.

What it costs is that a QA finding now blocks approval instead of arriving
after it, so things sit unapproved slightly longer. That is the entire
point.

## Feedback

If you run something like this and it fails differently, I'd like to hear:
[open an issue](../../issues).
