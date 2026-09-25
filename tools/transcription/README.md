# Transcription

Local audio-to-text. Point it at an audio or video file and get a timestamped transcript back, primed with your own glossary so names spell correctly.

The engine is [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (`whisper-cli`), not bundled; see [SETUP.md](SETUP.md). This tool is the wrapper: format conversion, glossary priming and output naming. **It has no network path**, not even as a fallback, because narrated recordings are usually more sensitive than they look.

## Known limits

- **Whisper mishears product nouns, confidently.** At `large-v3`, "Smooth Matte" became "smooth Mac" and "dual price" became "jewel price". A glossary fixes this; a bigger model doesn't.
- **`large-v3` fails silently in three ways.** On one 17-minute recording (427 segments): 28% of segments had zero duration, 36% repeated the previous segment, and the last 25 collapsed into 5 distinct sentences, a hallucination loop. The words read fine; the structure doesn't. Cross-check against a second model when timing matters.
- Timecodes drift by about half a second even on a clean run.
- No speaker labels.
- The install commands assume Homebrew. The tool itself isn't macOS-specific.
- The model is a one-time download of about 2.9 GB, never committed.

## Use

```bash
tools/transcription/transcribe.sh recording.mov              # no glossary, English
tools/transcription/transcribe.sh recording.mov my-project   # primed with a project glossary
```

Writes `<name>.transcript.txt` and `<name>.transcript.srt` beside the input. [`tools/video-frames/`](../video-frames/) reads the `.srt`.

| Env var | Default | Does |
|---|---|---|
| `WHISPER_MODEL` | `tools/whisper-models/ggml-large-v3.bin`, resolved from the script's location | Use a different model file |
| `WHISPER_LANG` | `en` | Language code; `auto` to detect |

## Glossaries

Whisper takes an initial prompt as context, so giving it the right spellings up front stops it guessing at ordinary English words. Two files feed it, in order:

1. `glossaries/_global.txt`, prepended to every run, for terms that recur across everything you record. Not shipped; create your own.
2. `glossaries/<project>.txt`, appended when you name a project.

**Order matters.** Whisper weights roughly the last 200 words of the prompt most heavily, so the project glossary goes last and the most important terms go at the bottom of each file. A glossary past a couple of hundred words starts pushing out its own best entries.

Start from [`glossaries/_template.txt`](glossaries/_template.txt). **Add only spellings you're sure of**: a wrong one biases the transcript toward the wrong spelling. Add any name you correct by hand, so the next recording doesn't repeat it.

## Two stages

1. **Whisper**: audio to text, primed as above. Fast, local, and wrong about names it has never heard.
2. **Cleanup by your model**: hand back the `.txt` with the full glossary and ask it to correct names from context. There's no 200-word limit here, so a long glossary pays off. The transcript goes to your model's provider at this stage. The script prints a reminder when it finishes.

## Defaults

| Default | Why |
|---|---|
| Converts to 16 kHz mono WAV first | What whisper.cpp expects; other inputs error or quietly lose accuracy |
| `ggml-large-v3` | Best on product names and accents. [SETUP.md](SETUP.md) has the case for starting smaller |
| Output beside the input | The transcript belongs with its recording |
| `-np` (no progress bar) | Keeps stdout clean for programs reading it |

## Setup

[SETUP.md](SETUP.md): three installs and one download. Or run `./setup.sh`, which does exactly what SETUP.md describes; `./setup.sh --dry-run` prints every command without running any.

Used by [`skills/video-review/`](../../skills/video-review/) and [`tools/video-frames/`](../video-frames/).
