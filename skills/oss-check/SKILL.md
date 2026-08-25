---
name: oss-check
description: Decide whether to ADOPT, VENDOR, STEAL-THE-PATTERN, PARK, or SKIP an external open-source project, skill, plugin, or MCP server. Reads the source, the package registry, the licence file and the push date rather than the README. Domain maturity caps the verdict but never cancels the search. Also hunts for candidates before you build something that smells solved. Load when handed a repo link, before installing any MCP server, skill, plugin or dependency, or when about to build from a blank page on a solved problem.
---

# OSS Check: Adopt, Vendor, Steal, Or Skip

## Purpose

Two failure modes, both cheap to avoid:

1. You build things that already exist, because nobody checked.
2. When you do reach for something external, you judge it from its README, which is marketing, written by the party that wants you to install it.

The principle underneath: **a README is what a project declares, which is not what it does.** Well-formed and confidently wrong is a whole class of failure, and it is precisely the kind that survives a casual look, because nothing about it appears broken. The checks below read the source, the package registry, the licence file and the push date instead.

The deliverable is **a verdict with receipts**. This skill installs nothing and adds no dependency. Adoption is a separate, human-approved step.

> **Known limits are real and stated.** Two gaps in Mode 2, and a live caveat on the search bias. Read [`README.md`](README.md#known-limits) before relying on the hunt mode.

## When To Use

Trigger phrases: `/oss-check`, "vet this repo", "should we use X", "is there something that already does this", "check before we build", "hunt for candidates".

Also fire **proactively** before:

- Installing any MCP server, skill, plugin, hook, output style, or rules file.
- Adding any dependency to something you ship.
- Starting from a blank page on something that smells solved (a date picker, a PDF validator, a scheduler, a diffing tool).

Do **not** run the full procedure for inert reference material: a research doc, a playbook, a design. Those need a source, licence and quality sanity-check, not an egress grep.

## Step 0: Read Your Register First

**Before any search, clone, or API call: read your register**, the running list of everything you have already evaluated and not adopted. Start one from [`register-template.md`](register-template.md) if you do not have one.

Two lookups:

- **Vetting a named candidate?** Search the **Repo** column. If it is there, you decided already. Read the reason and its revisit trigger before spending twenty minutes rediscovering it.
- **Hunting for a project?** Search the **Area** column. Something parked months ago may be exactly the thing.

A hit is not automatically final. Every row is dated and every SKIP carries a revisit trigger, because licences change, maintainers return and egress gets fixed. **If the trigger has fired, re-vet and update the row.**

This step is what makes the register worth keeping. **An index nobody reads is a document, not a check.** If you only ever write rows, delete the file and save yourself the effort. The reading is the whole mechanism.

## Step 0b: The Maturity Call (sets the verdict CEILING, never suppresses the search)

**Reuse pays in mature problem domains and loses in young ones.** A problem solved for decades has a category leader, a validator everyone accepts, and a maintenance base. A problem eighteen months old has a high abandonment rate, so ADOPT quietly means "inherit an abandoned dependency".

So maturity decides **how far a verdict can go**, not whether to look:

| Domain | Verdict ceiling |
|---|---|
| Mature, clear category leader, live maintenance | **ADOPT** is on the table |
| Young, churny, no category leader, high abandonment | **STEAL-THE-PATTERN**: read it, take the parts, depend on nothing |

**Always search. Always report what exists, with `pushed_at` beside every candidate.** "No candidate list" is not a valid outcome. Taking a dependency on a young repo carries ongoing maintenance risk; *reading its source* costs about an hour. Applying a dependency-sized brake to an hour of reading throws away the whole head start: the early steps, the dead ends someone already mapped, the week of getting-started time saved.

### Never use a star count as a maturity signal

**Stars measure how many developers are in a domain, not how good a repo is.** A "under 20 stars means the domain isn't ready" threshold really asks *"is this a popular developer topic?"* while appearing to ask *"is anything here any good?"* In a niche vertical the best thing in existence may have forty stars and still be the best thing in existence.

Worked example. A single search inside one narrow industry vertical returned two repos with **identical star counts of zero**: one pushed in 2025, one pushed in 2016. Identical on stars, completely different objects: one recent and worth an hour of reading, one nine years stale. **`pushed_at` separates them cleanly. The star count separates nothing.**

Use `pushed_at` and bus factor for liveness. Keep stars only as a weak tiebreaker between two live candidates *in the same domain*, and when reporting, say what counts as high for that vertical.

## Force A Verdict

"It looks good" is not a verdict. Every evaluation ends in one of five words. This is what stops an evaluation turning into a vibe.

| Verdict | Meaning | Where it lands |
|---|---|---|
| **ADOPT** | Install and depend on it. Requires a clean pass on every gate below. | A one-page written record |
| **VENDOR** | Copy the code in under your own control. For useful-but-unmaintained projects, or licences you cannot depend on live (AGPL in a product path). | A one-page written record |
| **STEAL-THE-PATTERN** | Read the source, write your own. The default for anything young, churny, licence-hostile, or context-injecting. | Inline, and **name the existing file the parts land in** |
| **PARK** | Good work, not useful now, worth finding again later. | Register row (area + revisit trigger) |
| **SKIP** | You decided against it. | Register **only if** re-deciding would cost real time *and* the surface looks clean; otherwise inline |

**Expect STEAL-THE-PATTERN to be the norm and ADOPT to be rare.** A STEAL verdict is a good outcome, not a disappointing one. Very rarely do you want something wholesale; usually there are small or large parts worth folding into what you already have.

**PARK is not the soft option.** It costs a register row with a real area and a real revisit trigger. If you cannot name both, the verdict is SKIP.

**Which SKIPs get indexed.** Most do not. A dead repo, the wrong language, an obvious licence blocker are all cheap to re-reject from the repo page, so indexing them is overhead. Index the ones where **you had to read the source to find the problem and nothing on the surface suggests it**, because the next person will otherwise redo that work in full.

---

# Mode 1: Vet A Named Candidate

## GATE-A: Never Probe With Real IP

If evaluating means calling the candidate's hosted service, **use a deliberately generic input**. Never send your own or your employer's product ideas, strategy, customer data, unreleased plans, or personal information to a third-party endpoint you are in the middle of deciding not to trust.

A candidate whose business model is logging your queries will log the probe.

## Phase 1: Identify The Artifact That Actually Installs

**The repo is not what runs on your machine.** `uvx foo` pulls from PyPI, `npx foo` from npm. Those can differ from the repo, and the publisher may not be the repo owner.

```bash
curl -s https://pypi.org/pypi/<pkg>/json | python3 -c "import json,sys; d=json.load(sys.stdin)['info']; print(d['version'],'|',d.get('author'),'|',d.get('home_page'),'|',d.get('project_urls'))"
npm view <pkg> --json 2>/dev/null | head -40
```

Confirm the published package points back at this repo, the publisher is the same org, and the latest published version matches the latest tag. **A mismatch is a finding, not a detail.**

## Phase 2: Maintenance And Trust Signals

```bash
gh api repos/OWNER/REPO --jq '{stars:.stargazers_count,watchers:.subscribers_count,forks:.forks_count,created:.created_at,pushed:.pushed_at,archived,license:.license.spdx_id}'
gh api repos/OWNER/REPO/contributors --jq '.[] | "\(.login)\t\(.contributions)"'
gh api users/OWNER/repos --jq '.[] | "\(.name)\tstars=\(.stargazers_count)\tpushed=\(.pushed_at[0:10])"'
```

Read them in this order:

- **`pushed_at` first.** A 22k-star repo last pushed ten months ago is dead. Stars are a historical artifact; the push date is the only liveness signal.
- **Watchers over stars.** Healthy is roughly 2–10% of the star count. Well under 1% on a young repo is an inflation **signal**, not proof. Write "signal", never "confirmed".
- **Bus factor.** One author with 187 commits and the next contributor at 2 is a single point of failure whatever the star count says. Org backing softens this; a lone individual does not.
- **Sibling repos.** A months-old org where one repo has 700+ stars and the rest have 0–60 is worth a raised eyebrow.
- **A stale parent may have a live fork.** See "Forks" under Mode 2 Phase 3. Do not call a project dead on the parent's push date alone.

Pull all of this **live**. Never work from memory about a repo's state: patterns drift, and a remembered star count or licence is usually subtly wrong in a way that reads as fact.

## Phase 3: Egress And Data Handling

The highest-value command in the method, because it answers the question the README will not:

```bash
gh repo clone OWNER/REPO /tmp/osscheck-<slug> -- --depth 1
grep -rnoE 'https?://[a-zA-Z0-9._/-]+' src/ | sort -u
grep -rniE 'telemetry|analytics|POST|upload|consent|opt.?in' src/ --include='*.py' --include='*.ts' --include='*.js'
```

Then answer explicitly:

1. **Does it send your input anywhere?** "Runs locally" and "local MCP stdio server" describe where the *process* runs, not where the *data* goes. Trace every POST to its URL.
2. **What is stored, and for how long?** Read the schema. A verbatim text column plus an embedding is a permanent record of what you asked, not a hashed metric.
3. **Do the linked policy files exist?** Fetch them. A disclaimer pointing at a privacy policy that 404s is a real finding and takes five seconds.
4. **Is there an escape hatch?** Many tools read an env var for their API base and fall back to a local path on failure, so pointing it at a dead address can neutralise the egress while keeping the function. **Verify that fallback exists in code** before promising it works.
5. **Does anything get injected into the agent's context?** Marketing calls-to-action, "next steps", or fetched remote text land in the context window and are a prompt-injection surface as well as an annoyance.
6. **Does it read credentials it has no reason to touch, and where is that enforced?** A tool that legitimately needs one API key has no business enumerating the environment, `~/.aws/`, `~/.ssh/`, `.env` files, the login keychain, or a password-manager vault. Distinguish **named** from **enumerated**: reading `OPENAI_API_KEY` is the job, walking `os.environ` is not.

   Note that this question has a precondition on *you*, not only on them: whatever is ambient in your own shell is in scope regardless of the candidate's hygiene. If your agent host injects a credential into every process it spawns, that is your exposure to fix before you evaluate anything.

   **Then ask the sharper half: does it scrub at the transport, or trust the call site?** A stated privacy contract is only as good as where it is enforced, and the two answers look identical while reading a single file. The weak form: a docstring promises that events never contain source code, file paths or query text, while the envelope builder forwards its `properties` argument verbatim, so the contract holds only while every current and future call site remembers it. The strong form, worth copying: one instrumentation path fans each event to a local logger at **full fidelity, never scrubbed**, and to telemetry through a strict **whitelist that silently drops any key not on it**, so a careless new call site cannot leak, and the rich local log and the minimal outbound copy cannot drift.

   **Prefer an allow-list at the transport over a promise at the call site**, and note which one you found. It is the difference between *"cannot send that"* and *"does not currently send that."*

```bash
grep -rniE 'os\.environ\b|process\.env\b|dotenv|keychain|security find-generic|\.aws/credentials|\.ssh/id_|netrc' src/ | head -30
```

7. **Is anything encoded rather than written?** Obfuscation is the one category a code read misses by construction, because the payload is not in a language you are reading. Look for base64 blobs, hex strings, `atob`/`Buffer.from(...,'base64')`, `eval` over a decoded string, or a long single-line literal. **Judge by whether the encoding has a reason**: an embedded PNG or a test fixture is fine, an encoded *command* or *URL* is not.

```bash
grep -rnoE '[A-Za-z0-9+/]{80,}={0,2}' src/ | head -20     # long base64-ish literals
grep -rniE 'atob\(|b64decode|base64 -d|base64 --decode|Buffer\.from\([^)]*base64|eval\(|exec\(|new Function\(' src/ | head -20
```

8. **If the candidate is an agent runtime, where does tool OUTPUT go, and is it scrubbed before it becomes prompt text?** Q6 asks what the tool *reads*. This asks the opposite direction, and **Q6 cannot catch it**: an agent runtime passes the environment to subprocesses and executes arbitrary commands **because that is its job**, so it never trips a "reads credentials it has no reason to touch" test. The exposure is *your* environment meeting an unscrubbed return path: command output, `read_file` contents and `execute_code` results flow back into the context window and out to whichever provider serves that turn.

   Ask three things: **(a)** is redaction applied to *every* tool-result path, or only to terminal output (a partial scrub is the common shape and reads as complete); **(b)** does it scope the child environment, or forward `os.environ` wholesale; **(c)** **which provider receives it**, because multi-provider routing means the cheap endpoint running an idle loop may be the one that receives a credential, and that is a different trust decision from the one you made when you picked the primary model.

   ```bash
   grep -rniE 'redact|scrub|sanitiz|mask|filter_secret|SECRET_PATTERN' src/ | head -20
   grep -rnB3 -A3 -E 'env=|environ\.copy\(\)|spawn|subprocess\.(run|Popen)|execFile|child_process' src/ | head -40
   ```

   **A spotless egress result says nothing about this**, because the data never leaves as an HTTP POST from their code. It leaves as prompt text, through the provider you configured. This is exfiltration whose transport is the model rather than the network.

## Phase 3B: The Context-Injection Gate (the one that matters most for skills and plugins)

**Read this phase as first-class, not a footnote.** Skills, plugins, rules files, output styles, hooks and MCP servers are not libraries, and **every code gate above passes trivially on them, because there is barely any code to check.** A clean egress grep on a skill proves nothing; it is a markdown file.

A skill or plugin is an **auto-updating prompt**, not code. So ask instead:

1. **Does it register an always-on hook** (`SessionStart`, `PreToolUse`, `UserPromptSubmit`) or does it only load when invoked? Always-on means it is in every session's context whether or not it is relevant.
2. **Does the install track a branch that updates without review?** A `git pull`-on-run install means tomorrow's context is not the one you vetted.
3. **Who can merge to that branch?** A repo taking community PRs is a repo where a stranger's text reaches your context window.
4. **Would you see the change before it lands?** If not, the vet has a shelf life of one commit.

**Default for context-injecting artifacts is STEAL-THE-PATTERN**: read it, take the rules you want into a file you control. **ADOPT only with a pinned ref that gets re-reviewed on every bump.**

Worked example. A skill repo with zero egress, an MIT licence, no published package and a careful fail-open opt-in hook was clean on every other gate. Still not an ADOPT, because the hook injects whatever the repo's `SKILL.md` says **at run time**, from a repo merging community PRs at 56 commits in a day.

Treat copied prose as untrusted instructions aimed at your agent, because that is exactly what it is.

## Phase 4: Read The Licence File, Then The Pricing Page

```bash
gh api repos/OWNER/REPO/contents/LICENSE.md --jq '.content' | base64 -d | head -50
gh api repos/OWNER/REPO/contents/LICENSE --jq '.content' | base64 -d | head -50
```

**Never trust GitHub's `.license.spdx_id` field.** It reports `NOASSERTION` for source-available licences carrying real commercial terms, which reads like "unknown" and is actually "there is a bill here".

**And the licence file is not the commercial picture either.** A licence can describe only an entity-size test while the vendor's pricing page separately sells a tier for automated or programmatic use that the licence text never mentions. A real example: a `LICENSE.md` describing a free-up-to-3-employees test, while the same vendor's pricing site sold an "Automators" tier at one hundred US dollars a month minimum for programmatic rendering. The two sources disagreed about whether a two-person company running an automated product owed nothing or twelve hundred US dollars a year.

Two independent sources that can disagree is a cross-check in licensing form. **When licence text and pricing page do not compose cleanly, say so and email the vendor** rather than picking the reading you prefer.

Check specifically:

- **Headcount, revenue, or usage caps**, and whether *automated or programmatic* use is carved out separately from headcount. For anything you would run as part of a product, assume that question exists until it has been ruled out.
- **AGPL.** Fine to read and to self-host internally, hostile in a product path. Usually turns ADOPT into STEAL-THE-PATTERN.
- **`NOASSERTION` with no licence file at all** is not permissive, it is unlicensed.

## Phase 5: Verdict, Routed Onto Real Work

State the verdict, the two or three findings that drove it, and **map it onto something you are actually doing**. A bare list of repos is worthless. The output that pays is *"this closes or shrinks that piece of work already on the list"*.

Forcing the mapping has a second benefit: it makes you check the recommendation against decisions you have already made, which is how you catch a suggestion that would quietly reopen something settled.

**Where the verdict is recorded:**

| Verdict | Record |
|---|---|
| **ADOPT** / **VENDOR** | A one-page record, because a dependency decision needs a receipt. Date, repo, findings, conditions. |
| **PARK** | A register row: date, repo, **area**, verdict, one sentence including what would bring you back. |
| **SKIP** (expensive, surface looks clean) | A register row, with the revisit trigger in the same sentence. |
| **STEAL-THE-PATTERN** | Inline. Name the **existing file** the parts land in, or say explicitly why a new one is warranted. |
| **SKIP** (obvious from the repo page) | Inline. One line. No register row. |

Keep register rows to one sentence. If a finding needs a paragraph, it is ADOPT/VENDOR-grade and belongs in its own record.

**If you stopped mid-vet, say which phases did not run, in the row itself.** A partial vet recorded as if complete is worse than no row, because the next reader inherits false confidence and skips the phases that would have found the problem.

---

# Mode 2: Hunt For Candidates

## Phase 1: Get The Spec. Two entry paths, and picking the wrong one wastes the sweep

**A. Something already exists** (a repo, a project folder, a running product): **derive, do not ask.** Read it yourself: component directories, design docs, lines of code per module. Asking the owner to scope the hunt costs a round trip and usually comes back "all of it". Only ask when two readings would produce genuinely different work.

**B. Nothing exists yet**: it is an idea, a problem, or a "can we do this better". **Then asking is the only source, and "derive, do not ask" does not apply.** There is nothing to read; deriving means inventing.

This distinction is worth stating because path A's instruction is correct and quietly stops being correct. A design decision carries a scope of validity that is recorded nowhere, so "do not ask" keeps looking deliberate long after the precondition that justified it has gone.

For path B:

1. **Sharpen the spec in conversation first.** A short discovery pass beats a long search against a vague brief. The sweep is only as good as the spec it runs against.
2. **Decompose into components**, and hunt per component rather than for the whole idea at once. Nobody sells your whole idea; several people sell its parts.
3. **Rename each component in the words that domain uses, not the words the owner used.** This is the step that decides whether the sweep finds anything. "A shared list my partner and I both see" finds nothing; "grocery list sync" finds a category. **Bad search terms are the main reason a hunt concludes "nothing exists" when something does.**
4. Then run Phase 2 and 3 per component.

The loop this sits inside is *sweep → vet → adapt*: search broadly for what exists, vet what looks promising, then adapt the thinking rather than installing the artifact. This skill is the vet half; path B is how the sweep half gets a spec to run against.

## Phase 2: Maturity Call Per Component

Apply Step 0b to each component **before** searching, to set that component's verdict ceiling. Young domain → the ceiling is STEAL-THE-PATTERN, so search and report what exists but recommend depending on none of it. **Never return an empty list for a component; "nothing here is worth depending on" and "nothing here is worth reading" are different findings.**

## Phase 3: Candidates With Live Metadata

```bash
gh search repos "<query>" --sort stars --limit 10 --json fullName,stargazersCount,pushedAt,description \
  --jq '.[] | "\(.fullName)\tstars=\(.stargazersCount)\tpushed=\(.pushedAt[0:10])\t\(.description // "" | .[0:80])"'
```

**Print `pushed_at` beside every candidate, always.** Probe named guesses directly with `gh api repos/OWNER/REPO`. A `NOT FOUND` is cheap and stops you recommending a repo that was renamed or never existed.

### Run three searches, not one

A single `--sort stars` search is structurally biased toward the establishment, so run all three:

```bash
# 1. The incumbents
gh search repos "<query>" --sort stars --limit 10

# 2. NEW WITH TRACTION: the closest thing to a "hot" or "trending" sort
gh search repos "<query>" --created=">YYYY-MM-DD" --stars=">100" --sort stars --limit 10

# 3. Forks only: where the live version of a stale project often lives
gh search repos "<query>" --include-forks only --sort updated --limit 10
```

**There is no trending sort.** `--sort` accepts exactly `forks`, `help-wanted-issues`, `stars`, `updated`, verified against the CLI, not remembered. GitHub runs a trending page on the web, but its ranking is not exposed as a sort you can call.

**Search 2 is the substitute, and it is arguably better.** A created-date window plus a star floor is *new with traction*: stars accumulated inside a bounded window is a rate, not a total. You choose the window, it is reproducible, and you can explain the ranking, none of which is true of a proprietary trending formula. Set the window to roughly the last three months and the floor to whatever counts as traction in that vertical.

This matters because search 1 cannot find these. A repo two months old with several thousand stars sits nowhere near the first page of a plain star sort, buried under projects that have been accumulating since 2019.

### Forks: a stale parent often has a live child

When a promising candidate's `pushed_at` looks dead, check whether someone is carrying it on:

```bash
gh api repos/OWNER/REPO/forks --jq 'sort_by(.pushed_at) | reverse | .[:5][] | "\(.full_name)\tpushed=\(.pushed_at[0:10])\tstars=\(.stargazers_count)"'
```

A fork sitting well ahead of an abandoned parent is frequently the real project. Judging liveness from the parent alone is a **false-negative** gap: it makes you discard things that are alive.

### Read the young ones for their disagreement

**A newer project built while an established one already exists encodes someone's opinion about what the established one got wrong**, *if they did their homework.* It is not a guarantee. Someone may simply not have looked before starting.

That gives you a tell worth checking rather than assuming: **does the project say what it is diverging from?** A young project that did the work usually says so out loud: "unlike X, this does Y", in the README, the docs, or the opening issue. One that names no alternative may have built in ignorance of them, and its divergence carries no information.

Where the divergence *is* stated, that statement is the finding. It is a free, specific critique of the incumbent from someone who cared enough to rebuild it.

## Phase 4: Vet The Shortlist

Run Mode 1 phases 3, 3B and 4 on anything you are about to call ADOPT. **A recommendation without the egress, context-injection and licence checks is not a recommendation.**

## Phase 5: Close It (Mode 2 does NOT end in a verdict)

Mode 1's Phase 5 does not fit here. A hunt ends in **three** things, all of them:

**1. A per-component verdict table.** One verdict *per component*, not one for the search.

| Component | Best candidate | Verdict | Why |
|---|---|---|---|

A component whose answer is "you already have this" gets a row saying so. So does one where the honest answer is "nothing here is worth depending on". That is a finding, and it is different from "nothing here is worth reading".

**2. What stays bespoke.** The explicit list of what nobody sells, and therefore what you build.

**This is the actual deliverable.** It is also the only part that is trustworthy *because* the sweep ran: before the sweep, "nobody sells this" is an assumption; after it, it is a finding. Never skip it because it feels like the leftovers. It is what the whole exercise was for.

**3. The synthesis that only appears when you see every candidate at once.** State it explicitly rather than leaving it implicit in the table.

Single-candidate verdicts cannot produce this, and it is the real argument for the hunt mode existing at all. A worked example: a sweep across five capability areas of a home-assistant project returned mature tools for four of them, and seeing them together produced the actual finding: **the tools were not rival apps to build against, but specialised backends to sit behind one conversational interface.** That resolved a standing design question ("one app or many?") the search had never been asked about. No individual verdict contained it.

**Then route it**, as Mode 1's Phase 5 requires: map the result onto work already queued, and check it against decisions already made.

---

## Gotchas

- **The README is the least reliable source in the repo.** It is marketing by the party that wants you to install.
- **Star counts age.** They record past attention, not current maintenance.
- **The package is not the repo.** Review what the install command actually pulls.
- **"Local" describes where the process runs, not where the data goes.**
- **Linked policy documents may simply not exist.** Always fetch them.
- **An MCP server's output is agent context.** Whatever it returns, including marketing copy, is inside the context window and inside the trust boundary.
- **GitHub's SPDX field is not the licence, and the licence is not the price.** Read the file, then the pricing page.
- **An empty search result is never evidence of absence.** Enumerate before concluding something does not exist. A check can "pass" because it never actually ran.
- **`gh api .../stargazers` with the timestamp Accept header 404s.** Do not burn calls trying to date the stars.
- **Writing your own slash command? Never put a bare dollar-zero or dollar-one token in the body.** The harness substitutes it with the invocation argument, which can silently rewrite a worked example mid-sentence with no error. This bites currency too: a price written with a dollar sign and a leading 1 is a substitution target, so write amounts and placeholders out in words. Note that backticks do not protect you, because the substitution is textual and does not know what markdown is.

## Core Constraints

1. **Read-only throughout.** This skill installs nothing, adds no dependency, and changes no config. Adoption is a separate, human-approved step.
2. **Force one of the five verdicts.** No "looks promising".
3. **GATE-A is absolute.** No real data into a candidate's endpoint or a search query.
4. **Live metadata only.** Never state a repo's stars, licence or push date from memory.
5. **Route the verdict onto live work** or the output does not pay.
6. **Record ADOPT and VENDOR; answer STEAL and SKIP inline.**
7. **A partial vet says so, in the record.**

## Anti-Patterns

- Reading the README and reporting what it says.
- Running the code gates on a skill or plugin and calling it clean. There is no code there. Run Phase 3B.
- Reporting a licence from GitHub's badge or SPDX field.
- Returning "no candidates, the domain is young" instead of a list. Search and report; let maturity cap the verdict.
- Using a star count as a quality bar. It measures the size of a domain's developer audience, nothing else.
- Skipping the register at Step 0 and re-deriving a verdict someone already paid for.
- Using PARK to avoid making a call. Without a real area and a real revisit trigger it is a SKIP.
- Recommending ADOPT without egress and licence checks.
- Installing during the vet "just to try it". The vet is read-only; trying it is adoption.
- Calling a project dead on the parent repo's push date without checking its forks.

## Still Open

Stated so you do not assume otherwise:

- **Mode 2 path B is a formalisation of practice, not a tested procedure.** The spec-first entry path (Phase 1B) and the three-part close (Phase 5) were written by reading back several hunts that worked and extracting what they had in common. That is a decent way to design something and it is *not* the same as having run the written version. Expect the wording to move.
- **The two modes share one file by choice, not by accident.** They produce different output shapes, one verdict versus a parts list, and each now has its own closing phase. Splitting them would duplicate every gate, which costs more than the seam does.
- **Mode 1 has no stated gaps.** That is not the same as having none. It has been run a few dozen times, not a few thousand.
