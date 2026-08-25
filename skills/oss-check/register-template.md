# OSS Check Register

Everything I have evaluated and **not adopted**, in one table. Written by `oss-check`, and read by it too, as the first step of any vet or hunt.

**This is the file Step 0 reads.** If rows only ever get written and never read, this file is doing nothing and the skill's first instruction is decoration.

## Two lookups

- **Vetting a named candidate?** Search the **Repo** column. A hit means it was already decided. Read the reason and the revisit trigger before spending twenty minutes rediscovering it.
- **Hunting for something?** Search the **Area** column. Something parked months ago may be exactly the thing. This is why Area is written as a *problem*, not as a product name.

**A hit is not automatically final.** Every row is dated and every SKIP carries a revisit trigger, because licences change, maintainers come back and egress gets fixed. If the trigger has fired, re-vet and update the row.

## What earns a row

| Verdict | Row? |
|---|---|
| **ADOPT** / **VENDOR** | No. These get their own one-page record. A dependency decision needs more than a sentence. |
| **PARK** | Yes. Requires a real area *and* a real revisit trigger. If you cannot name both, it is a SKIP. |
| **SKIP**: you had to read the source to find the problem, and nothing on the surface suggested it | Yes. This is the case that saves the most time later. |
| **SKIP**: obvious from the repo page (dead, wrong language, licence blocker) | No. Cheap to re-reject. A row costs more than it saves. |
| **STEAL-THE-PATTERN** | Only if the source is also worth finding again later. |

Keep rows to one sentence. If a finding needs a paragraph, it was ADOPT/VENDOR-grade and belongs in its own record.

**If a vet stopped early, say which phases did not run, in the row itself.** A partial vet recorded as complete is worse than no row, because the next reader inherits false confidence and skips exactly the checks that would have caught the problem.

## Split it later, not now

Deliberately one flat table. Most people do not evaluate many repos, and a single tight list is easier to scan than two. **If it gets long, split into a Parked section and a Skipped section** rather than adding columns or nesting. Do not pre-build that structure.

## Register

| Date | Repo | Area | Verdict | Reason (one sentence) |
|---|---|---|---|---|
| YYYY-MM-DD | [`owner/repo`](https://github.com/owner/repo) | The *problem* it solves, not the product category | PARK | Why not now, and the one thing that would bring you back. |
