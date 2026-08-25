# Decisions

## Why this exists

Every piece in this collection was extracted or rewritten from a private
workspace, which means every piece passed through some version of this
skill on its way out. Publishing the collection without the tool that
cleans it would leave the most-used step of the whole pipeline
undocumented. So it ships, last in the queue, with its limits stated
louder than its features.

## The condition this piece shipped under

The plan for the collection put one requirement on this skill: it ships
only after its scope and limits say plainly that it **rewrites content**
and is **not a release-assurance gate**.

The history behind that condition is worth recording. In my own workspace,
this skill drifted into doing double duty: it was the content-cleanup pass
and, in practice, it was being treated as the safety check, because a
clean change summary feels like clearance. Those are different jobs. The
content pass removes or generalises private context while preserving
usefulness; the release audit is deterministic scans plus human review
over the exact staged file set: git history, hidden files, symlinks,
ignored files, embedded image and document metadata, credential-pattern
scans, code egress behaviour, licences and adapted material, private or
broken links, and tests proving the genericised thing still works.

Publishing this skill as a complete safety solution would have been a
false claim about my own tool. The fix was not to make the skill do more;
it was to make the skill say less: the "What this is NOT" section is now
the second thing in the file, ahead of the procedure, and the what-not-to-
do list ends by refusing the exact misuse ("do not treat a clean pass as
permission to publish").

## The evidence that the two gates are different

The first time a real tool went through my full release path, the stages
beyond sanitisation found ten defects that already existed in the internal
copy: documentation commands that could not work when pasted, claims true
of one component written as claims about the whole, numbers that had
drifted between documents. Sanitisation had, correctly, found none of
them. Nothing about a name-and-path pass tests whether a command runs or
a claim holds. That asymmetry is the entire argument for the two-gate
model, and it is why this piece's README repeats it three times without
apology.

## What using it on this collection taught

The skill as published is the general-purpose pass. Working through this
collection's pieces added two practices on top of it, both worth stealing
even though neither is part of the skill itself:

- **A reviewer-only extraction audit per piece**: a file that classifies
  every source section as ported, adapted, or excluded, so the human
  review checks a mapping instead of re-deriving one.
- **A named inventory for the sensitive case**: for the one piece whose
  source contained genuinely confidential material, the audit listed every
  class of sensitive item and ran the list as literal greps over the
  output, with any hit a stop rather than a judgement call. A checklist
  you can grep beats a checklist you can only remember.

Both are the release-audit spirit applied early, and both exist because
the sanitisation pass alone kept proving insufficient in exactly the ways
the two-gate model predicts.

## What stayed home

Very little; the source was written close to public-shape already. The
internal version's pointer to my workspace's full publishing process
became the self-contained "What this is NOT" section, one trigger phrase
that named my public repo became generic, and the em dashes went. The
detection classes, replacement rules, placeholder block, and output
format ship essentially as they run internally.

## What I'd want pushed back on

- **Seven detection classes will not stay seven.** Industry-identifying
  worked examples and one-person quotes are the known gaps; there will be
  others. If something got through the pass for you, the class it belonged
  to is the feedback I want.
- **Placeholder style is a taste.** `[Your Company Name]` reads clearly
  but litters a document; some people prefer fictional consistent names.
  I chose visible placeholders because they cannot be mistaken for real
  content, which is also their cost.
- **Whether "do not over-sanitize" survives contact with fear.** The rule
  exists because the failure is real, but a nervous operator with a
  deadline will always strip too much. If you have found a way to make
  the keep-the-useful-stuff rule enforceable rather than advisory, that is
  the improvement this skill most needs.
