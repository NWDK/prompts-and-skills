# Decisions: three gates and a lock

## The order was wrong

Started mechanical-first: checklist, marker, QA after. The mechanical
pass surfaces most defects, so the item was least-verified when
approved, by the pass that certified its own fixes. Reordered: semantic
first, then QA (fresh session, no stake), then mechanical.

## Gate 0 doesn't get a number of its own

A side effect of the reorder above: the cheap checks and the lock shared
the last gate, so moving the tick moved the fastest feedback with it.
Splitting them out front doesn't add a gate: it settles and blocks
nothing.

## QA stays read-only about approval, not fixing

Letting QA fix what it finds is the obvious efficiency, rejected first:
a pass with an approval to produce has a stake in passing. Once its
full verdict is written and delivered it has nothing left to protect, so
it may fix what it found, on the owner's go, with a fresh session
re-checking.

## Reopening needs an external reason

Added after a component was unsigned on an argument that was thorough
and about nothing outside the system: every comparable component
handled its error state the same way, and nobody had checked whether
the state could occur. It couldn't; the build was reverted the same
day, caught from a screenshot. The fix: require the reason to point
outside the artefact.

## The lock is half the method

A verified artefact anything can quietly edit is a snapshot, not a
verification; the three properties came from real breakage, not design.
A waiver names the item and stays traceable; a silent skip is a false
clearance.

## The platform-specific checks stayed home

The internal version bundles ten further checks on top of this: real,
but publishing them well means a fixture proving each one, a project of
its own that would date fast.
