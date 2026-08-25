# Decisions: oss-check

What this is, where it came from, and the calls made along the way, including the ones that turned out wrong.

## Origin, and the credit

**This is adapted from a method by [@Ben-Eulogize](https://github.com/Ben-Eulogize)**, published August 2026 and used here with his permission. The method, the five-verdict structure and several of the sharpest checks are his. What I added was a register with a mandatory read step, the maturity-ceiling correction, and the search fixes in Mode 2.

His method came out of a real review, and the review is the reason any of this exists: **every material finding contradicted the reviewed project's README.** The disclaimer claimed no data was collected in local mode, while the code POSTed the full input to the vendor on every call. The privacy policy it linked to did not exist. Neither fact was hidden (both were one grep away) and neither was visible from the documentation.

**Then the useful part.** I ran his method on his method. It returned **STEAL-THE-PATTERN**, by its own rule about context-injecting artifacts: a skill is an auto-updating prompt rather than code, so you take the pattern into a file you control instead of installing something that can change under you.

So this skill is its own worked example. It was produced by the verdict it most often produces, applied to the thing that produced it. That was not a cute framing chosen afterwards. It is what the procedure returned when run honestly, and it is the single best argument for why STEAL-THE-PATTERN being the normal answer is a feature.

## Decisions

### The register has a mandatory read step, not just a write step

Early versions recorded verdicts. Recording is the easy half and it is worth almost nothing on its own: the value of knowing you already rejected something is only realised at the moment someone is about to re-reject it.

So Step 0 (read the register *before* any search, clone or API call) is the first instruction in the skill, ahead of everything else.

**The principle, which generalises well past this skill: an index nobody reads is a document, not a check.** Producing a signal and consuming it are separate acts, and by default only the first one gets built. If you write rows and never read them, delete the file; it is costing you effort and returning nothing.

### Star counts are rejected as a maturity signal entirely

An earlier version used a star threshold to decide whether a problem domain was mature enough to be worth searching. It read as sensible and it was measuring the wrong thing.

**Stars measure how many developers are in a domain, not how good anything in it is.** A threshold like "under 20 stars means this domain isn't ready" is really asking *is this a popular developer topic?* while appearing to ask *is anything here any good?* In a niche vertical the best thing in existence may have forty stars.

What settled it was two repos returned by the same search with identical star counts of zero: one pushed in 2025, one pushed in 2016. Same star count, completely different objects. **`pushed_at` separated them cleanly and the star count separated nothing.**

Stars survive only as a weak tiebreaker between two live candidates in the same domain.

### Maturity sets a ceiling, it does not suppress the search

The first version let a young, churny domain end the hunt: nothing here is stable enough, so do not bother. That is wrong, and it took a while to see why.

**Taking a dependency on a young repo is risky. Reading its source is not.** One carries ongoing maintenance cost; the other costs about an hour. Applying a dependency-sized brake to an hour of reading throws away the entire head start: the approaches already tried, the dead ends already mapped, the getting-started time already paid by someone else.

So maturity now caps how far a verdict can go and never decides whether to look. "No candidate list" stopped being a valid outcome.

### PARK must carry an area and a revisit trigger, or it is a SKIP

PARK was becoming the verdict you reach for when you do not want to make a call. Requiring both a real **area** (so the row is findable later by problem, not by name) and a real **revisit trigger** (so it can actually come back) made it expensive enough to mean something.

### Not every SKIP gets a row

Indexing every rejection makes the register long and unreadable, which kills the read step, which kills the register. **Index only the ones where you had to read the source to find the problem and nothing on the surface suggested it**. Those are the ones where the next person would otherwise redo the whole investigation. A dead repo or an obvious licence blocker is cheap to re-reject from the repo page.

### A partial vet has to say so, in the record

Added after parking a candidate mid-vet. A row that does not name the phases that never ran hands the next reader false confidence, and they will skip exactly the checks that would have found the problem. **A partial vet recorded as complete is worse than no row at all.**

### Three searches in Mode 2, not one

A plain `--sort stars` search is structurally biased toward incumbents, and I had been treating its output as "what exists".

Verified against the CLI rather than assumed: **`--sort` accepts only `forks`, `help-wanted-issues`, `stars` and `updated`. There is no trending sort**, and GitHub's trending page is not exposed as one.

The substitute is better than the thing it substitutes for. **A created-date window plus a star floor is "new with traction"** (stars accumulated inside a bounded window is a rate rather than a total), and unlike a proprietary trending formula, you choose the window, it reproduces, and you can explain it. Tested live: a search restricted to the previous three months with a 150-star floor returned several repos above 3,000 stars, **none of which appear anywhere near the first page of a plain star sort.**

The third search is forks-only, for the reason below.

### Liveness is judged on the parent *and* its forks

Reading `pushed_at` on the parent alone is a **false-negative** gap: it discards projects that are alive. When an original goes quiet, the living version is frequently somebody's fork carrying it on. `gh api repos/OWNER/REPO/forks` sorted by push date finds it in one call.

### The "young project encodes a disagreement" heuristic is conditional, and the condition is checkable

The observation: a newer project built while an established one already exists usually encodes someone's opinion about what the established one got wrong. Reading it for its disagreement is often more informative than reading the incumbent.

**It only holds if they did their homework**, which not everyone does. Someone may simply not have looked before starting, and then the divergence carries no information.

That is testable rather than assumed: **does the project say what it is diverging from?** A young project that did the work usually says so out loud: "unlike X, this does Y". One that names no alternative may have built in ignorance of them. This turned a heuristic into a check.

## Rejected

- **A numeric score.** Scores let you avoid deciding. Five words force a decision, and a verdict you cannot act on is a vibe with a number attached.
- **Splitting the register into parked and skipped tables.** Premature. One flat table is easier to scan until it is genuinely long; splitting by verdict is the right first move when that day comes, not adding columns or nesting.
- **Automating the verdict.** Every gate here produces evidence, not a conclusion. The step where a person looks at three findings and decides is the step that works.
- **Treating a clean egress result as a clean vet.** It is why Phase 3B exists as a first-class phase. On a skill or a plugin, every code gate passes trivially, because there is barely any code, and passing them proves nothing at all.
