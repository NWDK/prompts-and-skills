# OSS Check Register

Everything evaluated and **not adopted**, in one table. Read by `oss-check` as Step 0, before any search, clone or API call.

## Two lookups

- **Vetting a named candidate?** Search the **Repo** column. A hit means it was already decided: read the reason and revisit trigger before redoing the work.
- **Hunting for something?** Search the **Area** column, written as the *problem*, not a product name.

If a SKIP's revisit trigger has fired, re-vet and update the row.

## What earns a row

| Verdict | Row? |
|---|---|
| **ADOPT** / **VENDOR** | No. Gets its own one-page record instead. |
| **PARK** | Yes. Needs a real area *and* a real revisit trigger, or it's a SKIP. |
| **SKIP**, source-read required to find the problem | Yes. |
| **SKIP**, obvious from the repo page | No. Cheap to re-reject. |
| **STEAL-THE-PATTERN** | Only if worth finding again. Mark the state in the Verdict cell: `[STEAL-STATE: LANDED]`, `HELD YYYY-MM-DD`, or `DROPPED`. |

Keep rows to one sentence. If a vet stopped early, say which phases did not run, in the row itself.

## Split it later, not now

One flat table until it is genuinely long, then split into Parked and Skipped sections rather than adding columns.

## Register

| Date | Repo | Area | Verdict | Reason (one sentence) |
|---|---|---|---|---|
| YYYY-MM-DD | [`owner/repo`](https://github.com/owner/repo) | The *problem* it solves, not the product category | PARK | Why not now, and the one thing that would bring you back. |
