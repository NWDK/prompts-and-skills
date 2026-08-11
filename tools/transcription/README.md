# Transcription

Local audio-to-text. Point it at any audio or video file and get a timestamped transcript back, primed with your own glossary so names spell correctly.

Engine is [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (`whisper-cli`), which is not ours and is not bundled — see [SETUP.md](SETUP.md) for what to install. This tool is the wrapper: format conversion, glossary priming, and output naming.

**Everything runs on your machine. There is no network path in this tool** — not a setting, not a fallback. The reasoning is in [SETUP.md](SETUP.md) and it is the single most load-bearing design decision here.

## Known limits

- **Whisper mis-hears product nouns**, and it does so confidently. Two real misses at `large-v3`, the largest model: "Smooth Matte" → "smooth Mac", "dual price" → "jewel price". A glossary fixes these; a bigger model does not. Treat any odd-looking proper noun in the output as unconfirmed.
- **`large-v3` has three silent failure modes, and they are not rare.** Measured on one 17-minute screen recording, 427 segments:
  - **118 segments (28%) came back with zero duration** — start and end timecode identical. They claim a moment rather than a span.
  - **155 segments (36%) repeated the previous segment**, either verbatim (35) or as a prefix the next line carries forward (120). Read as prose it looks like a stutter; parsed as data it inflates the transcript.
  - **The last 25 segments collapsed to 5 distinct sentences**, one of them repeating to the end of the file. That is a hallucination loop, not dropped audio.

  None of this raises an error, and none of it looks wrong on a casual read — the words are right, the structure is not. If timing matters, cross-check against a second model rather than trusting one run.
- **Timecodes drift by roughly half a second** even on a clean run, on top of the above.
- **No speaker labels.** The output is one undifferentiated stream, so a two-person interview comes back without any marker of who is talking.
- **The install commands assume Homebrew**, i.e. macOS. Nothing in the tool itself is macOS-specific; the packages exist on Linux under other names.
- **The model is a ~2.9 GB download** you make once. It is not in this repo and never will be.

## Use

```bash
# Simplest form: no glossary, English
tools/transcription/transcribe.sh recording.mov

# Primed with a project glossary (see below)
tools/transcription/transcribe.sh recording.mov my-project
```

Writes `<name>.transcript.txt` and `<name>.transcript.srt` next to the input file. The `.srt` is the one `tools/video-frames/` consumes.

| Env var | Default | What it does |
|---|---|---|
| `WHISPER_MODEL` | `tools/whisper-models/ggml-large-v3.bin` | Use a different model file. The default is resolved from the script's own location, so the tool works in any checkout. |
| `WHISPER_LANG` | `en` | Language code. `auto` to detect. |

## Glossaries, and why the ordering matters

Whisper accepts an initial prompt, and it uses that prompt as context for what it is about to hear. Give it the right spelling of a product name up front and it stops guessing at the nearest ordinary English words.

Two files feed it, in this order:

1. `glossaries/_global.txt` — prepended to every run. For terms that recur across everything you record. **Not shipped here**, because yours would be nothing like anyone else's; create it if you want it.
2. `glossaries/<project-name>.txt` — appended, when you name a project.

**The order is the whole design.** Whisper weights roughly the **last 200 words** of the primer most heavily, so the project glossary goes last because it is the more specific one, and within a file the most-likely terms go at the bottom. A glossary that has grown past a couple of hundred words has started evicting its own most important entries.

Start from [`glossaries/_template.txt`](glossaries/_template.txt) — it carries the two rules that make a glossary help rather than hurt. The important one:

> Only add spellings you are **sure** of. A wrong spelling actively biases the transcript toward the wrong spelling, which is worse than no glossary at all.

Harvest as you go. Any name you correct by hand belongs in the glossary afterwards, or the next recording in the same domain repeats the same mistake.

## Two-stage by design

1. **Whisper** does audio → text, primed as above. Fast, local, and wrong about names it has never seen.
2. **Claude** does a context-aware cleanup: hand back the `.txt` along with the full glossary and ask it to correct names against context. No 200-word cap at this stage, so this is where a long glossary earns its keep.

Stage 2 is a documented part of the tool, not a workaround for stage 1 being imperfect. The script prints a reminder when it finishes.

## Non-obvious defaults

| Default | Why |
|---|---|
| Converts everything to 16 kHz mono WAV first | What whisper.cpp expects. Skipping it produces either an error or quietly worse accuracy depending on the input. |
| `ggml-large-v3` | Best available on product names and accented speech, which is where the failures actually are. [SETUP.md](SETUP.md) has the full size table and the case for starting smaller. |
| Output lands beside the input | The transcript belongs with the recording. Nothing is written to a central directory you then have to go find. |
| `-np` (no progress bar) | Keeps stdout clean for anything reading the output programmatically. |

## Setup

First run on a machine → **[SETUP.md](SETUP.md)**. Three installs and one download.

Or run `./setup.sh` from this directory, which does exactly what SETUP.md describes and nothing else. Read it first — `./setup.sh --dry-run` prints every command without running any of them.

## Used by

- [`skills/video-review/`](../../skills/video-review/) — turns a recording into a cited written document
- [`tools/video-frames/`](../video-frames/) — consumes the `.srt` to label frames with what was being said
