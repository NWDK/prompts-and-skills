# Decisions: oss-check

What this is, where it came from, and the calls made along the way.

## Origin, and the credit

Adapted from a method by **[@Ben-Eulogize](https://github.com/Ben-Eulogize)**, used with permission. The method, the five-verdict structure and several of the sharpest checks are his, from a review where every finding contradicted the project's README (a "no data collected locally" claim, while the code POSTed the full input on every call; a linked privacy policy that did not exist). Added since: the mandatory register read, the maturity-ceiling correction (now a dependency-mode table with VENDOR as a real option), the Mode 2 search fixes, the fork-ratio check, and the STEAL resolution step. Running the method on itself returns STEAL-THE-PATTERN, by its own rule.

## Decisions

**The register has a mandatory read step, not just a write step.** A recorded verdict pays off only when someone is about to re-reject the same thing. Step 0 (read before any search, clone or API call) is the skill's first instruction: an index nobody reads is a document, not a check.

**Star counts are rejected as a maturity signal.** "Under 20 stars" really asks whether a topic is popular with developers, not whether anything in it is good. What settled it: two repos from one search with identical zero star counts, one pushed in 2025, one in 2016; `pushed_at` separated them, stars did not. Stars survive only as a tiebreaker between two live candidates in the same domain.

**Maturity sets a ceiling, it does not suppress the search.** An early version let a young domain end the hunt. Wrong: a dependency on a young repo is risky, but reading its source costs about an hour, and a dependency-sized brake on an hour of reading throws away a real head start. Maturity caps the verdict; it never decides whether to look.

**The ceiling table had two rows and no middle.** Mature-or-young quietly lost VENDOR: a review of past verdicts found it had never once been chosen, because the table gave it nowhere to land. Fix: reframe the question from "good enough to depend on" to "can this change what reaches me without me seeing it first". A live dependency can; a frozen, reviewed-on-bump copy cannot, whatever its age. Three rows now, keyed on whether the source was read, not on age. One thing does not loosen with age: an unpinned install path, since an old project has more people who can push into what you auto-pull, not fewer.

**A high fork-to-star ratio means the parent is the wrong thing to read.** The existing fork check only rescues a stale parent and cannot fire on a healthy repo, which is exactly where a widely recommended project (forks running roughly a third of its stars) got vetted twice without anyone checking whether a fork had already filled the gap found in the parent. Fix: a ratio of roughly 20%+ signals fork-and-own distribution; enumerate the network sorted by stars, not push date, and conclude in terms of the network. Different from the liveness check, which fires on a stale parent: this fires on a healthy one.

**PARK must carry an area and a revisit trigger, or it is a SKIP.** PARK was becoming the verdict for avoiding a call. A real area (findable by problem) and a real revisit trigger (so it can come back) make it cost enough to mean something.

**Not every SKIP gets a row.** Indexing every rejection makes the register long and unreadable, killing the read step. Index only the ones where a source read was needed to find the problem; a dead repo or obvious licence blocker is cheap to re-reject.

**A STEAL verdict has to resolve to a state, not just name a file.** ADOPT and VENDOR get a written record, PARK and SKIP a register row; STEAL produced only a chat message, and past verdicts included real cases where a file was named and the edit never made. Fix: STEAL now resolves to LANDED (made now, the default), HELD (deferred, with a named reader and date), or DROPPED. The record must also name the pattern taken, not only the verdict.

**A partial vet has to say so, in the record.** An unlabelled partial row hands the next reader false confidence and lets them skip the checks that would have found the problem.

**Three searches in Mode 2, not one.** A plain `--sort stars` search is structurally biased toward incumbents. Verified against the CLI: `--sort` accepts only `forks`, `help-wanted-issues`, `stars` and `updated`; there is no trending sort. Substitute: a created-date window plus a star floor is "new with traction", a rate rather than a total. Tested live: three months plus a 150-star floor surfaced repos above 3,000 stars invisible to a plain star sort. Third search: forks-only.

**Liveness is judged on the parent and its forks.** `pushed_at` on the parent alone is a false-negative gap: when an original goes quiet, the living version is often a fork carrying it on, found in one `gh api .../forks` call sorted by push date.

**The "young project encodes a disagreement" heuristic is conditional, and checkable.** A newer project beside an established one usually encodes an opinion about what the incumbent got wrong, but only if the author did their homework. Testable rather than assumed: does the project say what it diverges from ("unlike X, this does Y")? One naming no alternative may have built in ignorance of it.

## Rejected

- **A numeric score.** Scores let you avoid deciding. Five words force a decision.
- **Splitting the register into parked and skipped tables.** Premature; one flat table is easier to scan until it is genuinely long.
- **Automating the verdict.** Every gate produces evidence, not a conclusion; the step where a person weighs three findings is the step that works.
- **Treating a clean egress result as a clean vet.** On a skill or plugin, every code gate passes trivially, because there is barely any code; Phase 3B exists because passing them proves nothing.
