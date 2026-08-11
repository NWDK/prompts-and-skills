# Setup — video-frames

Two commands. Nothing is downloaded beyond standard packages, and there is no model file for this tool.

```bash
brew install ffmpeg
python3 -m pip install Pillow
```

| | What it is | Why it's needed |
|---|---|---|
| **ffmpeg** | The standard command-line tool for reading and converting audio and video | Reads the video and writes the frames |
| **ffprobe** | Ships with ffmpeg, same install | Reads the real duration, resolution and frame rate. The tool never assumes these. |
| **Pillow** | A Python library for reading and resizing images | Compares frames to decide whether the screen actually changed |

Python 3 itself is assumed — `python3 --version` should print something. macOS ships it.

Not on macOS? ffmpeg is packaged everywhere; only the `brew` line is macOS-specific.

If `pip` refuses because your Python is externally managed (PEP 668), either `python3 -m pip install --user Pillow` or install into a virtualenv. The tool does not care which, as long as `import PIL` works for the `python3` you invoke it with.

## Check it works

```bash
python3 tools/video-frames/extract.py probe <any video file>
```

You should get the duration, resolution, frame budget and an estimated token cost. It writes nothing.

Each dependency fails with its own fix in the message, so if something is missing you will be told which command to run rather than shown a stack trace.

## If you are also using transcription

[`tools/transcription/`](../transcription/SETUP.md) needs `whisper-cpp` and a model file on top of these. Its setup covers ffmpeg and Pillow as well, so run that one instead and you are done for both. `video-review` uses both tools together.
