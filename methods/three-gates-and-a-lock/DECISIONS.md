# Decisions: three gates and a lock

## The order was wrong, and I was the one who got it wrong

This started as mechanical-first: run the deterministic checklist, apply
the marker, QA afterwards. That order failed in a specific way. The
mechanical pass is genuinely the thing that surfaces most defects, so the
item was at its least-verified precisely when it got approved, and the same
pass that found the defects then certified its own fixes.

My own note at the time: *until we run the full sign-off and get the tick,
it doesn't discover half the issues. We then discover some of them, and
then, after we finally run QA, we discover yet more issues.*

Reordered to semantic first (it produces changes, so let the rework happen
before the passes that check it), QA second (fresh session, no stake),
mechanical last (it's the lock, so it sits closest to the approval).

Worth recording because I misremembered the order when I came to write this
up, and reached for the version I had already replaced. Reading the process
rather than recalling it is the only reason this piece is right.

## QA stays read-only, and that was the contested part

The obvious efficiency is to let QA fix what it finds. It's already looking,
it knows what's wrong, and a separate correction pass costs another round.

Rejected, twice, for reasons that both turned out to be load-bearing. A
pass that knows it must produce an approval has a stake in passing, and
QA's entire value is having no outcome to protect. And keeping one writer
keeps one audit trail: markers written in one place, cleanup run in one
place, the record emitted in one place.

## Version-specific clearance, with no tolerance

"The item changed slightly since QA read it" is the most reasonable-sounding
way for this to fail. Any change voids the clearance. No "still basically
the same".

This is the rule that stops the gate becoming a formality, and it's also
the one that annoys people most, including me.

## The lock is half the method

The gates get the attention, but a verified artefact that anything can
quietly edit afterwards is not verified, it's a snapshot. Approval has to
freeze the thing, or the approval is a claim about the past.

Three properties came out of real breakage rather than design: it survives
permissive modes (running an agent with expanded permissions authorises
tool use, not changes to approved work), sub-agents inherit it and must
escalate rather than decide, and authorisation covers one named item, one
session, one described change.

## Waivers are recorded, not silent

Skipping a gate is allowed, because sometimes it has to be. The distinction
that matters is between a waiver and a gap: a waiver names the item, gets
recorded, and leaves the thing traceable as unverified. A silently skipped
gate produces a false clearance, which is worse than no clearance.

## The Figma checks stayed home

The internal version bundles this process with ten platform-specific
checks: how publish state actually behaves, when a component isn't the copy
it appears to be, what makes text silently carry two fonts.

Those are real, and I use them daily, but publishing them well would mean
building a capability matrix (which of these are readable via the plugin
API, which via REST, which need judgement) and a test fixture to prove
each one. That's a project, and it would date fast.

The process is the transferable half and it needs no such validation. If
the checks ever ship, they ship as an appendix to this, not the other way
round.
