#!/usr/bin/env bash
# Local audio transcription via whisper.cpp with per-project context priming.
# Engine: whisper-cli (whisper.cpp, brew). Model: ggml-large-v3 (local, nothing uploaded).
#
# Usage:
#   transcribe.sh <audio-file> [project-name]
#
# Examples:
#   transcribe.sh ~/Downloads/client-call.m4a
#   transcribe.sh ~/Downloads/walkthrough.mp4 my-project
#
# Context priming: glossaries/_global.txt is prepended when it exists. If a
# project name is given, glossaries/<project-name>.txt is appended. Both are
# optional; with neither, whisper runs unprimed. The combined text is fed
# to whisper as the initial prompt so names/spellings transcribe correctly.
# whisper only uses ~the last 200 words of the prompt, so keep glossaries tight
# and put the most important / most likely names last.
#
# Output: <audio-basename>.transcript.txt and .srt, written next to the audio file.
# Stage 2 (optional but recommended): hand the .txt back to Claude with the full
# project glossary for a context-aware cleanup pass on any remaining mangled names.

set -euo pipefail

TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Resolved from this script's own location, not an absolute path, so the tool
# works in any checkout rather than only the machine it was written on. Override
# with WHISPER_MODEL to use a different size — see SETUP.md for the tradeoff.
MODEL="${WHISPER_MODEL:-$TOOL_DIR/../whisper-models/ggml-large-v3.bin}"
LANG_CODE="${WHISPER_LANG:-en}"
GLOSS_DIR="$TOOL_DIR/glossaries"

die() { echo "Error: $*" >&2; exit 1; }

[ $# -ge 1 ] || die "usage: transcribe.sh <audio-file> [project-name]"
AUDIO="$1"
PROJECT="${2:-}"

[ -f "$AUDIO" ] || die "audio file not found: $AUDIO"
[ -f "$MODEL" ] || die "model not found: $MODEL
  First run on this machine? See tools/transcription/SETUP.md — one command downloads it.
  Already have a model elsewhere? Point at it:  export WHISPER_MODEL=/path/to/ggml-*.bin"
command -v whisper-cli >/dev/null || die "whisper-cli not installed. Run: brew install whisper-cpp   (see tools/transcription/SETUP.md)"
command -v ffmpeg >/dev/null || die "ffmpeg not installed. Run: brew install ffmpeg   (see tools/transcription/SETUP.md)"

# Build the context primer: global glossary first, project glossary last (last = highest weight).
PROMPT=""
[ -f "$GLOSS_DIR/_global.txt" ] && PROMPT="$(grep -vE '^\s*#' "$GLOSS_DIR/_global.txt" | tr '\n' ' ')"
if [ -n "$PROJECT" ]; then
  PFILE="$GLOSS_DIR/${PROJECT}.txt"
  if [ -f "$PFILE" ]; then
    PROMPT="$PROMPT $(grep -vE '^\s*#' "$PFILE" | tr '\n' ' ')"
  elif [ -n "$PROMPT" ]; then
    echo "Note: no glossary for project '$PROJECT' ($PFILE). Using the global glossary only." >&2
  else
    # Neither glossary exists, so whisper runs unprimed. Say that plainly rather
    # than implying a fallback that is not there, and name the fix.
    echo "Note: no glossary for project '$PROJECT' ($PFILE), and no _global.txt either." >&2
    echo "      Running unprimed — expect product and people names to be mis-heard." >&2
    echo "      To fix: cp $GLOSS_DIR/_template.txt $PFILE" >&2
  fi
fi
PROMPT="$(echo "$PROMPT" | tr -s ' ' | sed 's/^ //;s/ $//')"

# whisper.cpp wants 16kHz mono WAV. Convert whatever was passed in.
TMPWAV="$(mktemp -t whisper).wav"
trap 'rm -f "$TMPWAV"' EXIT
echo "Converting audio to 16kHz mono WAV..." >&2
ffmpeg -nostdin -loglevel error -y -i "$AUDIO" -ar 16000 -ac 1 -c:a pcm_s16le "$TMPWAV"

OUT_PREFIX="${AUDIO%.*}.transcript"
echo "Transcribing with large-v3 (lang=$LANG_CODE)..." >&2
[ -n "$PROMPT" ] && echo "Context primer: ${PROMPT:0:160}..." >&2

whisper-cli \
  -m "$MODEL" \
  -f "$TMPWAV" \
  -l "$LANG_CODE" \
  ${PROMPT:+--prompt "$PROMPT"} \
  -otxt -osrt \
  -of "$OUT_PREFIX" \
  -np

echo ""
echo "Done."
echo "  Transcript: ${OUT_PREFIX}.txt"
echo "  Timestamped: ${OUT_PREFIX}.srt"
echo ""
echo "Stage 2 (recommended): give ${OUT_PREFIX}.txt to Claude and ask for a"
echo "context-aware cleanup using the full ${PROJECT:-<project>} glossary."
