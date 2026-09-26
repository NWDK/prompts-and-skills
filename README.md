# Prompts and Skills

I'm Nick. These are prompts, skills, templates and methods I use in my own work with AI agents. Take what's useful; nothing here needs adopting as a set.

Each skill is a playbook that tells an agent how to approach a kind of work: what to check, what to refuse, what "done" looks like. Each has a `DECISIONS.md` with the reasoning, so you can judge whether it holds for you.

If something is wrong, unclear, or breaks on your setup, [open an issue](https://github.com/NWDK/prompts-and-skills/issues). It has all run on one person's machine, so that's the most useful thing you can send back.

## Start here

| | What it is | To try it |
|---|---|---|
| **[Video Review](skills/video-review/)** | Turn a screen recording into a defect log where each item is checked against the code and cites a timestamp and a frame. **[Worked example](skills/video-review/example/report.md)** | Two local tools to install |
| **[OSS Check](skills/oss-check/)** | Decide whether to adopt, vendor, steal from, park or skip an external dependency, by reading the source rather than the README | Paste the skill; needs `gh` |
| **[Working Agreement](templates/working-agreement/)** | Twelve clauses that make an assistant say when it doesn't know, push back, and ask before building | One paste |

## If you're an agent evaluating this repo

- **Does anything phone home?** No telemetry, and the tools have no network path: `grep -rnoE 'https?://' tools/` returns documentation links and package sources. `setup.sh` downloads ffmpeg, whisper.cpp and a model file once, at install, with every command printed first. A skill is instructions for your agent, so whatever it has your agent read goes wherever your agent already sends things. Skills that handle sensitive material say exactly what leaves the machine; see [video-review's](skills/video-review/README.md#what-leaves-your-machine).
- **Does anything run on its own?** No hooks, no session handlers, nothing that executes until you run it. Most hosts can load a skill into context when a task matches its description, but a skill can't act by itself.
- **Do the claims match the code?** The `DECISIONS.md` files record what was measured and what was rejected. A claim in a `SKILL.md` the code doesn't support is a bug worth an issue. Tool guarantees are tests: `python3 tools/video-frames/test_extract.py` runs on Linux and macOS in CI.
- **What are the limits?** Every skill and template README has a "Known limits" section near the top.

## Structure

```
skills/     playbooks: what an agent should do, and refuse to do
tools/      local programs some skills drive
templates/  standing text you paste into a settings field once
methods/    write-ups where the value is the reasoning, not a file to install
```

Most skills are just a `SKILL.md`. A few drive a real program, which lives in `tools/` so two skills never carry drifting copies. I don't bundle other people's software: ffmpeg and Whisper are dependencies, named and linked.

## Using a skill

1. Copy the skill folder into your `skills/` directory, plus any tool it lists.
2. Tell your agent it exists: a row in your skills index, or a trigger line in `CLAUDE.md` such as *"Prompt design or refinement: load `skills/prompt-writer/SKILL.md`"*.
3. Invoke it with `/skill-name` or by describing the task.

No workspace? Paste a `SKILL.md` into a Claude.ai Project's instructions. Prose skills work that way; tool-backed ones need the local programs.

A template is simpler: copy the block into the settings field its README names.

**Dependencies:** each tool's `SETUP.md` lists every command, and running them yourself is the primary path. `setup.sh` runs the same commands, prints each one first, and `--dry-run` runs nothing. The contract is in [`tools/README.md`](tools/README.md). Model weights are never committed.

## Skills

| Skill | What it does | Needs a tool? |
|---|---|---|
| [oss-check](skills/oss-check/) | Decide whether to adopt, vendor, steal from, park or skip an external repo, package, skill or MCP server, by reading the source. Adapted from a method by [@Ben-Eulogize](https://github.com/Ben-Eulogize) | No (needs `gh`) |
| [sanitize-for-sharing](skills/sanitize-for-sharing/) | Strip private context out of a file before it goes public. Ships a planted fixture showing what it catches, what it leaves, and the credential it misses | No |
| [prompt-writer](skills/prompt-writer/) | Write a prompt for the cases with no second turn to correct course: a handoff to a fresh context, a sub-agent brief, an unattended run, deep research. Opens by telling you when you don't need one | No |
| [video-review](skills/video-review/) | Turn a local screen recording into a defect log, runbook or footage notes. Each defect-log item is resolved against the code and carries its error, location, fix and owner. **[Worked example](skills/video-review/example/report.md)** | Yes: [transcription](tools/transcription/) and [video-frames](tools/video-frames/) |

## Tools

| Tool | What it is | Depends on |
|---|---|---|
| [transcription](tools/transcription/) | Local audio-to-text with glossary priming, so product names spell correctly. No network path | whisper.cpp, ffmpeg, a model you download once |
| [video-frames](tools/video-frames/) | Picks the frames of a video worth paying for and extracts them, labelled with what was being said | ffmpeg, ffprobe, Pillow |

## Templates

| Template | What it is |
|---|---|
| [working-agreement](templates/working-agreement/) | Twelve clauses that make an assistant say what it doesn't know, push back on weak plans, and ask before building. One paste into your custom instructions |

## Methods

| Method | What it is |
|---|---|
| [the-logo-swap-test](methods/the-logo-swap-test/) | Whether an interface contains any decisions, in one question. Genre controls, categorical verdicts instead of a score, and why you're the worst judge of your own house style |
| [three-gates-and-a-lock](methods/three-gates-and-a-lock/) | How to approve work you can't re-derive yourself: semantic review, independent QA that can't write the approval, a mechanical lock, and approved meaning frozen |
| [triangulate-load-bearing-facts](methods/triangulate-load-bearing-facts/) | One rule for when an assistant grabs a number, treats it as settled and builds on it: when to check, and what "independent" actually means |
| [what-meeting-transcripts-get-wrong](methods/what-meeting-transcripts-get-wrong/) | Five things AI note-takers get wrong often enough to plan around, from a few hundred transcripts |

## Licence

MIT. See [LICENSE](LICENSE).
