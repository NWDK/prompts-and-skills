# Setup — first run on a new machine

Three things to install. **Transcription itself runs entirely on your machine and uploads nothing** — that is the point of the tool. (Setup does download the programs and a model file over the network, once. And if you then hand the transcript to a cloud model for the optional cleanup pass, that text goes to your provider like anything else you send it.)

Run these from the root of your copy of this repo. If you have put the tools somewhere else, adjust the paths to match.

## 1. The programs

```bash
brew install whisper-cpp ffmpeg
python3 -m pip install Pillow
```

| | What it is | Why it's needed |
|---|---|---|
| **whisper-cpp** | Runs OpenAI's Whisper speech-to-text model on your own machine, no internet | Turns the audio into a timestamped transcript |
| **ffmpeg** | The standard command-line tool for reading and converting audio and video | Pulls the audio out of the recording, and extracts frames for `tools/video-frames/` |
| **Pillow** | A Python library for reading and resizing images | Compares frames to decide whether the screen actually changed |

Not on macOS? `whisper-cpp` and `ffmpeg` are both packaged for most Linux distributions, and whisper.cpp builds from source in a couple of minutes. Nothing here is macOS-specific except the `brew` line itself.

## 2. The model

Whisper is a *trained model*: a single large file of numbers the program reads to turn sound into words. It has to be downloaded once.

```bash
mkdir -p tools/whisper-models
curl -L -o tools/whisper-models/ggml-large-v3.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin
```

`transcribe.sh` looks for the model at `tools/whisper-models/ggml-large-v3.bin`, resolved relative to the script's own location rather than to wherever you happen to be standing. Keeping it there means the tool works in any checkout. Put it elsewhere and point at it with `WHISPER_MODEL`.

### Why this runs locally at all

There are cloud transcription APIs that need no download and no install. This tool deliberately does not use one, and it is worth understanding the reason rather than assuming nobody considered it.

**The audio in a screen recording is usually more sensitive than it looks.** Someone narrating a walkthrough is talking over unreleased features, pre-launch campaigns, landing pages that are not live, customer data on screen. "It's only a marketing page" is exactly the assumption that gets something uploaded that should not have been — and the person recording rarely stops to make that call mid-sentence.

So the tool has no network path at all. Not a setting, not a fallback. That costs a download; it buys never having to make that judgement under time pressure.

### Which size to get

This is the real choice, and it is yours. Bigger is more accurate, slower, and more disk.

| Model | Size | Where it lands |
|---|---|---|
| `ggml-base.en` | ~150 MB | Clear speech, ordinary words, no unusual names. Downloads in seconds. |
| `ggml-small.en` | ~500 MB | Noticeably better on hesitant or fast speech. |
| `ggml-medium.en` | ~1.5 GB | Strong. English only. |
| `ggml-large-v3` | **~2.9 GB** | Best on product names, brand nouns, accents and mumbling. Multilingual. |

Swap the filename in the URL above, then point the tool at it:

```bash
export WHISPER_MODEL=/full/path/to/ggml-base.en.bin
```

**How to choose.** If the recording is mostly plain speech, start small — you will know inside one recording whether it holds up, and moving up is one more download. If it is full of product names, brand terms, or people's names, start at `medium.en` or `large-v3`, because those are exactly what small models mangle.

### If the transcript comes back rough

Reach for these **before** downloading a bigger model. Both are cheaper and both fix the most common problem, which is not mishearing sentences but mangling *names*.

1. **A glossary.** Priming the model with the right spellings fixes most name errors before they happen. Two real misses from a product walkthrough, transcribed at `large-v3`, the biggest model available: "Smooth Matte" came out as "smooth Mac", "dual price" as "jewel price". A bigger model would not have fixed those; a glossary does. See step 3.
2. **The cleanup pass.** Hand the transcript back to Claude along with the glossary and ask it to correct names against context. This is a documented second stage of the tool, not a workaround.

A small model plus a good glossary routinely beats a large model with none. Judge accuracy *after* both, not before.

> The model file is deliberately **not** committed to any repo, and `.gitignore` here blocks `*.bin` so it cannot be added by accident. A 2.9 GB binary in version control makes every clone slow forever, and it quietly makes whoever committed it responsible for someone else's release cadence. It is one of the standing checks in [tools/README.md](../README.md).

## 3. A glossary (optional, 2 minutes, big payoff)

Whisper mis-hears names it has never seen. Priming it with the right spellings fixes most of that before it happens.

Copy the template and fill it in:

```bash
cp tools/transcription/glossaries/_template.txt \
   tools/transcription/glossaries/my-project.txt
```

Then run with the project name:

```bash
tools/transcription/transcribe.sh recording.mov my-project
```

Only add spellings you are **sure** of. A wrong spelling in the glossary actively biases the transcript toward the wrong spelling, which is worse than not having one.

There is a second, optional glossary at `glossaries/_global.txt`, prepended to every run whatever project you name. It is for the handful of terms that recur across everything you record — your own company name, the people who are always on the call, the fonts you always argue about. This repo ships without one, because yours would be entirely different to anyone else's. Create it the same way if you want it, or skip it and the tool runs on the project glossary alone.

## Check it works

```bash
tools/transcription/transcribe.sh <any short audio or video file>
```

You should get a `.transcript.txt` and a `.transcript.srt` beside the input file. If something is missing, the error names the exact command to fix it.
