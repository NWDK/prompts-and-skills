# Tools

Local programs that some skills drive. Most skills are just a `SKILL.md` and need nothing here.

A tool lives in this directory rather than inside the skill that uses it, so two skills needing the same thing share one copy instead of each carrying a version that drifts.

## What a tool in here is, and is not

**Is:** a small program written for this repo — usually a wrapper that drives something standard like ffmpeg, plus the judgement about how to drive it.

**Is not:** ffmpeg, Whisper, Python libraries, or anything else with its own maintainers. Those are dependencies, named and linked, never bundled. Vendoring someone else's software into a repo claims an authorship you do not have and quietly makes you responsible for their security updates.

## What every tool here must carry

| File | Why |
|---|---|
| `README.md` | What it does, **known limits near the top**, and the reasoning behind non-obvious defaults |
| `SETUP.md` | Every dependency, what it is in plain English, why it is needed, and the exact install command |
| `setup.sh` | Optional. Runs exactly what `SETUP.md` describes, nothing more |

If a default is a specific number, the README says how it was arrived at. A threshold with a measurement behind it is a decision; the same number without one is a guess wearing a lab coat.

## The install-script contract

An install script is exactly the shape of thing you should be suspicious of in someone else's repo, and pretending otherwise would be silly. So the rules here are deliberate:

1. **The manual path is primary.** `SETUP.md` lists every command in plain English. The script is a convenience for people who do not live in a terminal, not the supported route.
2. **`--dry-run` prints the commands and exits.** Read them, run them yourself, never execute the script at all. That is a legitimate way to use this repo.
3. **Every command is echoed before it runs.** No silent steps.
4. **Nothing is piped from the internet into a shell.** No `curl … | bash`, ever. Downloads land in a file you can inspect.
5. **The script does only what `SETUP.md` already describes.** Anything else is a bug, not a feature.
6. **Nothing runs with `sudo`.** If a tool genuinely needs elevated permissions, the doc says so and you run that line yourself.

A script that follows all six is readable in about a minute. Reading it is encouraged; the point is that you do not *have* to trust it, because you can always take path 2.

## Adding a tool

- Keep it to one job. A tool that both transcribes and edits is two tools.
- No network calls unless the tool's entire purpose is a network call, and then say so in the first line of the README.
- Fail with the fix in the message. `whisper-cli not installed. Run: brew install whisper-cpp` beats a stack trace.
- Sanitise before it lands here: no absolute paths, no employer-specific names, no internal links. See `skills/sanitize-for-sharing/` if you have it.
