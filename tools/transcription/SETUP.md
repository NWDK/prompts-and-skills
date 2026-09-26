# Setup: first run on a new machine

Three things to install. Transcription runs on your machine and uploads nothing. Setup downloads the programs and a model file once, and the optional cleanup pass sends the transcript to your model's provider.

Run these from the root of your copy of this repo, or adjust the paths.

## 1. The programs

```bash
brew install whisper-cpp ffmpeg
python3 -m pip install Pillow
```

| | What it is | Why |
|---|---|---|
| **whisper-cpp** | OpenAI's Whisper speech-to-text model, run locally | Turns audio into a timestamped transcript |
| **ffmpeg** | The standard command-line audio and video tool | Pulls audio out of recordings, and extracts frames for `tools/video-frames/` |
| **Pillow** | A Python image library | Compares frames to decide whether the screen changed |

Not on macOS? Both programs are packaged for most Linux distributions, and whisper.cpp builds from source in a couple of minutes. Only the `brew` line is macOS-specific.

## 2. The model

Whisper needs a trained model file, downloaded once:

```bash
mkdir -p tools/whisper-models
curl -L -o tools/whisper-models/ggml-large-v3.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin
```

`transcribe.sh` looks for it there, relative to its own location, so it works in any checkout. Put it elsewhere and set `WHISPER_MODEL`. `.gitignore` blocks `*.bin`, so the model can't be committed by accident.

### Which size

| Model | Size | Good for |
|---|---|---|
| `ggml-base.en` | ~150 MB | Clear speech, ordinary words |
| `ggml-small.en` | ~500 MB | Hesitant or fast speech |
| `ggml-medium.en` | ~1.5 GB | Strong, English only |
| `ggml-large-v3` | ~2.9 GB | Product names, brand nouns, accents. Multilingual |

Swap the filename in the URL, then `export WHISPER_MODEL=/full/path/to/ggml-base.en.bin`.

Mostly plain speech? Start small; one recording will tell you. Full of product or people's names? Start at `medium.en` or `large-v3`.

**If the transcript comes back rough, try these before a bigger model.** Most errors are mangled names, not misheard sentences. A glossary (step 3) fixes most of them up front, and the cleanup pass ([README](README.md#two-stages)) fixes the rest. A small model with a good glossary routinely beats a large one without.

## 3. A glossary (optional)

```bash
cp tools/transcription/glossaries/_template.txt \
   tools/transcription/glossaries/my-project.txt
tools/transcription/transcribe.sh recording.mov my-project
```

Add only spellings you're sure of; a wrong one biases the transcript toward it. For names that recur across everything you record (your company, regular colleagues), create `glossaries/_global.txt` the same way. It's prepended to every run.

## Check it works

```bash
tools/transcription/transcribe.sh <any short audio or video file>
```

You should get a `.transcript.txt` and a `.transcript.srt` beside the input. If something is missing, the error names the command that fixes it.
