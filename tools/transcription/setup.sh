#!/usr/bin/env bash
#
# Installs what SETUP.md describes, and nothing else.
#
# THE MANUAL PATH IS THE PRIMARY ONE. SETUP.md lists every command in plain
# English and you can run them yourself in about a minute. This script exists
# because typing five commands correctly is a real barrier for people who do
# not live in a terminal. It is not the supported route, it is a convenience.
#
# What it will and will not do:
#   - Every command is printed before it runs. There are no silent steps.
#   - --dry-run prints the commands and exits without running any of them.
#     Reading them and running them yourself is a legitimate way to use this.
#   - Nothing is piped from the internet into a shell. The one download lands
#     in a file you can inspect before anything reads it.
#   - Nothing runs with sudo. If a step needs elevated permissions it will
#     fail and tell you, rather than asking for your password.
#   - Anything already installed is skipped.
#
# Usage:
#   ./setup.sh                      # install using the default model
#   ./setup.sh --dry-run            # print the commands, run nothing
#   ./setup.sh --model ggml-base.en # a smaller model; see SETUP.md for sizes

set -euo pipefail

DRY_RUN=0
MODEL_NAME="ggml-large-v3"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --model)
      [ $# -ge 2 ] || { echo "error: --model needs a name, e.g. --model ggml-base.en" >&2; exit 2; }
      MODEL_NAME="$2"; shift ;;
    -h|--help) sed -n '2,23p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "error: unknown option $1 (try --help)" >&2; exit 2 ;;
  esac
  shift
done

# Resolved from this script's own location, so it works from any directory.
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$TOOL_DIR/../whisper-models"
MODEL_PATH="$MODEL_DIR/${MODEL_NAME}.bin"
MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/${MODEL_NAME}.bin"

say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
skip() { printf '   skip: %s\n' "$*"; }

# Print the command, then run it. In --dry-run, print only.
run() {
  printf '   $ %s\n' "$*"
  if [ "$DRY_RUN" -eq 0 ]; then "$@"; fi
}

if [ "$DRY_RUN" -eq 1 ]; then
  say "DRY RUN — printing the commands below. Nothing will be executed."
  say "Run them yourself if you would rather not execute this script at all."
fi

# --- 1. the programs ---------------------------------------------------------
# SETUP.md step 1: brew install whisper-cpp ffmpeg / python3 -m pip install Pillow

step "Programs (SETUP.md step 1)"

if ! command -v brew >/dev/null 2>&1; then
  say "error: Homebrew is not installed, and it is how SETUP.md installs these."
  say "  Install it from https://brew.sh, or install whisper-cpp and ffmpeg by"
  say "  whatever means your platform prefers, then re-run. Both are packaged"
  say "  for most Linux distributions under the same names."
  exit 1
fi

BREW_WANTED=()
command -v whisper-cli >/dev/null 2>&1 && skip "whisper-cpp already installed" || BREW_WANTED+=("whisper-cpp")
command -v ffmpeg      >/dev/null 2>&1 && skip "ffmpeg already installed"      || BREW_WANTED+=("ffmpeg")

if [ ${#BREW_WANTED[@]} -gt 0 ]; then
  run brew install "${BREW_WANTED[@]}"
fi

if python3 -c "import PIL" >/dev/null 2>&1; then
  skip "Pillow already installed"
else
  # Deliberately the same command SETUP.md prints. If your Python is
  # externally managed (PEP 668) this will refuse, and the fix is yours to
  # choose — a virtualenv, or --user, or your system package manager.
  if ! run python3 -m pip install Pillow; then
    say ""
    say "error: pip refused to install Pillow."
    say "  Most often this is an externally-managed Python (PEP 668). Either:"
    say "    python3 -m pip install --user Pillow"
    say "  or create a virtualenv and install there. SETUP.md has the context."
    exit 1
  fi
fi

# --- 2. the model ------------------------------------------------------------
# SETUP.md step 2: mkdir the model directory, curl the model into it.

step "Model (SETUP.md step 2): ${MODEL_NAME}"

if [ -n "${WHISPER_MODEL:-}" ]; then
  say "   WHISPER_MODEL is set to: $WHISPER_MODEL"
  if [ -f "${WHISPER_MODEL}" ]; then
    skip "that file exists, so no download is needed"
  else
    say "   warning: that path does not exist. Unset WHISPER_MODEL to use the"
    say "   default location, or download a model to that path yourself."
  fi
elif [ -f "$MODEL_PATH" ]; then
  SIZE="$(du -h "$MODEL_PATH" 2>/dev/null | cut -f1 || echo '?')"
  skip "model already at $MODEL_PATH (${SIZE})"
  say "   If that size looks wrong, an earlier download was interrupted:"
  say "   delete the file and re-run."
else
  say "   Downloading to a file, not piping anything into a shell."
  say "   This is a large download — see the size table in SETUP.md."
  run mkdir -p "$MODEL_DIR"
  run curl -L -o "$MODEL_PATH" "$MODEL_URL"
fi

# --- 3. a glossary -----------------------------------------------------------
# SETUP.md step 3 is optional and needs a name only you can choose, so this
# script points at it rather than guessing one on your behalf.

step "Glossary (SETUP.md step 3, optional)"
say "   Two minutes here saves correcting the same names on every recording:"
say ""
say "   cp $TOOL_DIR/glossaries/_template.txt \\"
say "      $TOOL_DIR/glossaries/my-project.txt"
say ""
say "   Then pass the name:  transcribe.sh recording.mov my-project"

# --- done --------------------------------------------------------------------

if [ "$DRY_RUN" -eq 1 ]; then
  step "Dry run complete. Nothing was installed or downloaded."
  exit 0
fi

step "Done. Check it works:"
say "   $TOOL_DIR/transcribe.sh <any short audio or video file>"
say ""
say "   You should get a .transcript.txt and a .transcript.srt beside it."
