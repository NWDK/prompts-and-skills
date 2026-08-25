# oss-check

Decide whether to **adopt, vendor, steal the pattern from, park, or skip** an external repo, package, skill, plugin or MCP server, by reading the source, the package registry, the licence file and the push date, rather than the README.

It answers two questions:

- *Should we use this thing someone just sent me?* (Mode 1)
- *Has someone already solved this, before I build it?* (Mode 2)

The output is a verdict with receipts. The skill installs nothing and changes no config.

## Known limits

Read these before relying on it.

- **The hunt mode's spec-first path is a formalisation of practice, not a tested procedure.** Phase 1B (starting from an idea rather than a repo) and Phase 5 (how a hunt closes) were written by reading back several hunts that worked and extracting what they had in common. That is a reasonable way to design something, and it is not the same as having run the written version. Expect the wording to move.
- **Mode 1 has no stated gaps. That is not the same as having none.** It has been run a few dozen times, not a few thousand.
- **It is a review procedure, not a security guarantee.** A determined supply-chain attack is not what this catches. What it catches is the ordinary, common case: a project whose README describes something the code does not do.
- **Obfuscation is a partial check by construction.** Phase 3 Q7 looks for encoded payloads, but if the payload is not in a language you are reading, a source read is the wrong instrument.
- **It assumes `gh` is authenticated** against a GitHub account. Nothing here works against GitLab, Codeberg or a private forge without rewriting the commands.
- **The register is yours to keep.** The skill's first step reads a register of past verdicts. If you never write rows, or never read them, Step 0 does nothing. That is the most likely way this fails in practice: not a wrong verdict, just an unused one.

## Compatibility

- **Any agent host with shell access.** The procedure is markdown; the checks are shell commands.
- **Needs:** `gh` (GitHub CLI, authenticated), `grep`, `curl`, `python3` for the JSON one-liners, and `npm` only if you are vetting an npm package.
- **No install and no dependency it adds to your project.** Every command is one you could type yourself.
- **It does make network calls, by design.** `gh` and `curl` fetch public metadata and source from GitHub, npm and PyPI. They read public data and send nothing of yours. The one exception it guards deliberately: GATE-A forbids probing a candidate's own hosted endpoint with real material, because that would put your input on someone else's server as the price of vetting them.

## Using it

**Copy-paste, no installation.** Paste `SKILL.md` into any capable model along with the repo URL, and ask it to run the procedure. The commands are yours to run; the model reads the output and forces a verdict. This works fine and is the fastest way to try it.

**Installed in an agent workspace.** Copy this folder into your `skills/` directory, add a row wherever your setup indexes skills, and add a trigger line so your agent loads it, something like *"Adopting anything external, or hunting for candidates before building: load `skills/oss-check/SKILL.md`."* Then invoke with `/oss-check <repo url>` or just ask.

**Start a register.** Copy [`register-template.md`](register-template.md) somewhere durable. It is the file Step 0 reads. One flat table is correct until it is long; do not pre-build a structure for it.

## A worked invocation

> **You:** `/oss-check https://github.com/some-org/some-skill-pack`

The agent should:

1. **Read your register first.** If the repo is already there, it reports the existing verdict and its revisit trigger, and stops. Nobody re-derives a decision that was already paid for.
2. **Set the ceiling.** Agent-skill packs are a young domain with no category leader, so the ceiling is STEAL-THE-PATTERN before it has looked at anything. It still looks.
3. **Pull live metadata.** Stars, watchers, forks, created, pushed, contributors. Never from memory.
4. **Run the gates.** Egress grep, credential-read grep, the context-injection questions, then the licence file (not the badge).
5. **Force one of five words**, name the two or three findings that drove it, and say which file of yours the stolen parts land in.

A realistic ending looks like this:

> **STEAL-THE-PATTERN.** Clean on every code gate: zero egress, real MIT file, no published package. Not an ADOPT because its hook injects whatever the repo's `SKILL.md` says at run time, from a repo merging community PRs at 56 commits a day, so the vet has a shelf life of one commit. Taking its two best checks into your own review file. Register row written with the revisit trigger: *if they start pinning reviewed refs.*

Note what that is not. It is not "looks solid, 4/5". A verdict you cannot act on is a vibe with a number attached.

## The bit that surprises people

**Expect STEAL-THE-PATTERN to be the normal answer, and ADOPT to be rare.** That feels like failure the first few times. It is not. Reading someone's source and taking the two ideas that matter costs an hour and leaves you owning your own code. Adopting costs an hour too, and leaves you owning a dependency, its abandonment risk, and its licence.

The corollary is the part worth internalising: **a young domain caps the verdict, it never cancels the search.** "Nothing here is worth depending on" and "nothing here is worth reading" are completely different findings, and only the first one is usually true.

## Origin

Adapted from a method by **[@Ben-Eulogize](https://github.com/Ben-Eulogize)**, with his permission. See [`DECISIONS.md`](DECISIONS.md) for what was taken, what was changed, and the review that produced it.
