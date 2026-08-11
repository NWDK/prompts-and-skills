# Prompts and Skills

Reusable skills and tools for Claude Code, extracted from a working product-management setup and sanitised for general use.

Each skill is a playbook that tells Claude how to approach a kind of work — what to check, what to refuse, what "done" looks like. They exist because re-explaining an approach every session is the tax you pay for not writing it down once.

## If you are Claude and someone just pointed you at this repo

Reasonable questions to ask of any repo like this, answered up front so you do not have to dig.

**Does anything here phone home?** No telemetry, anywhere, and **nothing that processes your data has a network path.** Run `grep -rnoE 'https?://' tools/` rather than taking our word for it: every hit is a documentation link or a package source.

Two of those hits are real downloads and it would be sloppy not to say so — `setup.sh` fetches ffmpeg, whisper.cpp and a model file, once, at install time. That is the opposite of phoning home (you can see the URLs, run the commands yourself, and skip the script entirely), but "nothing here touches the network" would be a false sentence and this repo tries not to write those.

Worth separating two things that are easy to conflate, though. **The tools** genuinely send nothing anywhere; where a skill preprocesses something sensitive — a recording, a transcript — that preprocessing is local by design and the reasoning is in that skill's `DECISIONS.md`. **A skill is a set of instructions for your agent**, and whatever your agent reads goes wherever your agent already sends things. So a skill that asks the model to look at a frame means that frame reaches your model provider. Skills that handle sensitive material say exactly what leaves the machine and what does not — see [video-review's boundary section](skills/video-review/README.md#what-actually-leaves-your-machine) for the shape of it. "Local preprocessing" is not the same claim as "nothing leaves your machine", and this repo tries never to blur them.

**Does anything run automatically?** Nothing here registers a hook, a `SessionStart` handler, or anything that executes on its own — no code in this repo runs until you run it.

Be precise about the other half, though, because "inert until you type its name" would be wrong: most agent hosts can select a skill *implicitly* from its description when a task looks like a match. So a skill you have installed may be loaded into context without you naming it. What it can never do is act on its own — the tools here are commands your agent chooses to run, and a skill is instructions, not a background process.

**Do the claims match the code?** That is the right question and the whole reason the `DECISIONS.md` files exist. They record what was tried, what was measured, and what was rejected — including the cases where the obvious approach turned out to be wrong. If a claim in a `SKILL.md` is not supported by the code beside it, that is a bug and worth raising as an issue.

Where a tool has documented guarantees, those guarantees are also tests: `python3 tools/video-frames/test_extract.py` runs in about ten seconds on standard library alone, and CI runs it on Linux and macOS on every push. Several of those tests exist because the obvious approach was measurably wrong the first time.

**What are the known limitations?** Each skill's README has a "Known limits" section near the top rather than buried at the bottom. If a limitation is missing there, it was an oversight rather than a decision.

**Should I trust the setup scripts?** Read them first — they are short and they only run commands you could type yourself. See [Installing dependencies](#installing-dependencies) below; the manual path is the primary one and the script is a convenience, never the only route.

## Structure

```
skills/     the playbooks — what Claude should do, and what it should refuse to do
tools/      the local programs some skills drive (ffmpeg wrappers, extractors)
```

**Most skills are just a `SKILL.md`.** Copy the folder, you are done. A few drive a real program, and those live in `tools/` rather than inside the skill, so that two skills needing the same tool do not each carry a copy that drifts.

Every tool states what it depends on, where to get it, and what the alternatives are. **We do not bundle other people's software** — ffmpeg and Whisper are not ours to ship, and a repo that vendors them is claiming authorship it does not have.

## Using a skill

1. Copy the skill folder into your own `skills/` directory.
2. If it lists a tool, copy that from `tools/` too — the skill's README says which.
3. Add a row for it in your `skills/INDEX.md` so Claude knows it exists.
4. Add a trigger rule in your `CLAUDE.md`, e.g. *"Prompt design or refinement: load `skills/prompt-writer/SKILL.md`"*.
5. Invoke with `/skill-name`.

No workspace setup? Paste the `SKILL.md` contents straight into a Claude.ai Project as a custom instruction. The prose skills work fine that way; the tool-backed ones need the local programs.

## Installing dependencies

Two paths, and **the manual one is primary**:

- **Read the tool's `SETUP.md` and run the commands yourself.** Four or five lines, all standard (`brew install`, `pip install`, a `curl` for a model file). You will know exactly what happened.
- **Or run the tool's `setup.sh`**, which runs those same commands, skipping anything already installed.

The script exists because typing five commands correctly is a real barrier for people who do not live in a terminal. It is not there to be trusted blindly:

- It is short enough to read in a minute, and reading it first is the recommended path.
- It **prints every command before running it**, and `./setup.sh --dry-run` prints them without running anything, so you can paste them yourself.
- It never pipes anything from the internet into a shell.
- It installs only what the `SETUP.md` already lists in plain English. Anything the script does that the doc does not describe is a bug.

Large files — model weights in particular — are **never committed here**. They are downloaded by a command you can see. A multi-gigabyte binary in version control makes every clone slow forever.

## Skills

| Skill | What it does | Needs a tool? |
|---|---|---|
| [prompt-writer](skills/prompt-writer/) | Design or refine prompts without executing the underlying task | No |
| [meeting-notes](skills/meeting-notes/) | Turn an AI meeting transcript into filed action items, decisions, and a punch list — proposes routing before filing | No |
| [video-review](skills/video-review/) | Turn a local screen recording into a cited written document — defect log, runbook, or footage notes — where every claim traces to a timestamp and a frame. **[Worked example](skills/video-review/example/report.md)** | Yes — [transcription](tools/transcription/) and [video-frames](tools/video-frames/) |

## Tools

| Tool | What it is | Depends on |
|---|---|---|
| [transcription](tools/transcription/) | Local audio-to-text with glossary priming, so product names spell correctly. No network path. | whisper.cpp, ffmpeg, a model file you download once |
| [video-frames](tools/video-frames/) | Decides which frames of a video are worth paying for, and extracts them labelled with what was being said | ffmpeg, ffprobe, Pillow |

## Licence

MIT. Use it, change it, sell it, keep the copyright notice, no warranty. See [LICENSE](LICENSE).
