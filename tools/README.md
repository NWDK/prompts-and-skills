# Tools

Local programs that some skills drive. Most skills are just a `SKILL.md` and need nothing here. Tools live here rather than inside a skill, so two skills that need the same one share a single copy.

A tool here is a small program written for this repo, usually a wrapper around something standard like ffmpeg, plus the judgement about how to drive it. ffmpeg, Whisper and Python libraries are dependencies: named and linked, never bundled.

## Every tool carries

| File | Contents |
|---|---|
| `README.md` | What it does, known limits near the top, and how each non-obvious default was arrived at |
| `SETUP.md` | Every dependency, what it is in plain English, why it's needed, and the exact install command |
| `setup.sh` | Optional. Runs exactly what `SETUP.md` describes |

## The install-script contract

1. **The manual path is primary.** `SETUP.md` lists every command; the script is a convenience.
2. **`--dry-run` prints the commands and exits**, so you can run them yourself and never execute the script.
3. **Every command is echoed before it runs.**
4. **Nothing is piped from the internet into a shell.** Downloads land in a file you can inspect.
5. **The script does only what `SETUP.md` describes.**
6. **Nothing runs with `sudo`.** If something needs it, the doc says so and you run that line yourself.

## Adding a tool

- One job per tool.
- No network calls unless the network call is the tool's purpose, and then say so in the README's first line.
- Fail with the fix in the message: `whisper-cli not installed. Run: brew install whisper-cpp`.
- If it writes into a directory the user chose, test that it leaves the rest of that directory alone. `video-frames/test_extract.py` is the example: standard-library `unittest`, fixtures generated at run time, and assertions about what must not have happened.
- No absolute paths, employer names or internal links. See [`skills/sanitize-for-sharing/`](../skills/sanitize-for-sharing/).
