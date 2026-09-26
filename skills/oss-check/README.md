# oss-check

Decide whether to **adopt, vendor, steal the pattern from, park, or skip** an external repo, package, skill, plugin or MCP server, by reading the source, the package registry, the licence file and the push date rather than the README.

Answers two questions: *should I use this thing someone sent me* (Mode 1), and *has someone already solved this, before I build it* (Mode 2). Output is a verdict with receipts. Installs nothing, changes no config.

## Known limits

- Mode 2's spec-first hunt path (Phase 1B, Phase 5) is a formalisation of practice, not a tested procedure; wording may move.
- Mode 1 has no stated gaps, which is not the same as having none.
- It is a review procedure, not a security guarantee: it catches a README that does not match the code, not a determined supply-chain attack.
- Obfuscation (Phase 3 Q7) is a partial check: a source read is the wrong instrument for a payload that is not in a readable language.
- Assumes `gh` is authenticated. Nothing here works against GitLab, Codeberg or a private forge without rewriting the commands.
- The register is yours to read as well as write. If you never read it, Step 0 does nothing.

## Compatibility

- Any agent host with shell access. The procedure is markdown; the checks are shell commands.
- Needs: `gh` (authenticated), `grep`, `curl`, `python3`, and `npm` if vetting an npm package.
- No install, no dependency added to your project.
- Makes network calls by design: `gh` and `curl` fetch public metadata from GitHub, npm and PyPI. The exception is GATE-A, which forbids probing a candidate's own hosted endpoint with real material.

## Using it

**Copy-paste:** paste `SKILL.md` into any capable model along with the repo URL and ask it to run the procedure.

**Installed in an agent workspace:** copy this folder into your `skills/` directory, index it, and add a trigger line so your agent loads it. Invoke with `/oss-check <repo url>` or just ask.

**Start a register:** copy [`register-template.md`](register-template.md) somewhere durable. It is the file Step 0 reads.

## A worked invocation

> **You:** `/oss-check https://github.com/some-org/some-skill-pack`

The agent should:

1. Read your register first; stop if the repo is already decided.
2. Set the ceiling (a young domain starts at STEAL-THE-PATTERN, but a clean source read can still earn VENDOR).
3. Pull live metadata, never from memory.
4. Run the gates: egress, credentials, context-injection, then the licence file.
5. Force one of five words, name the findings, and for a STEAL say what happened to the parts.

A realistic ending:

> **STEAL-THE-PATTERN.** Clean on every code gate: zero egress, real MIT file, no published package. Not an ADOPT because its hook injects whatever `SKILL.md` says at run time, from a repo merging community PRs at 56 commits a day. Taking its two best checks into your own review file, landed now.

That is not "looks solid, 4/5". Expect this ending to be normal: reading someone's source and taking the two ideas that matter costs about an hour and leaves you owning your own code; adopting costs an hour too and leaves you owning a dependency.

## Origin

Adapted from a method by **[@Ben-Eulogize](https://github.com/Ben-Eulogize)**, with his permission. See [`DECISIONS.md`](DECISIONS.md) for what changed and why.
