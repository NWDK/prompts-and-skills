#!/usr/bin/env bash
#
# Regenerates the worked example in this directory, end to end.
#
#   ./make-example.sh
#
# Builds a synthetic 24-second "screen recording" of a fake checkout page with
# three deliberate defects, runs the real extraction pipeline over it, and leaves
# the manifest and frames behind. The report beside this script was written from
# those frames by hand, following SKILL.md, and is not regenerated here — the
# writing step is the model's job, which is the entire point of the skill.
#
# Nothing here is a mock. `extract.py` is the shipped tool with the shipped
# defaults, and the numbers in the report come out of it.
#
# Requires ffmpeg and Pillow (see ../../../tools/video-frames/SETUP.md).
# Transcription is NOT run: it needs a 2.9 GB model, so a hand-written .srt of
# the narration is committed instead. Everything downstream of it is real.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACT="$HERE/../../../tools/video-frames/extract.py"
VIDEO="$HERE/checkout-walkthrough.mp4"
FRAMES="$HERE/checkout-walkthrough-frames"

command -v ffmpeg >/dev/null || { echo "ffmpeg not installed. Run: brew install ffmpeg"; exit 1; }
[ -f "$EXTRACT" ] || { echo "cannot find extract.py at $EXTRACT"; exit 1; }

echo "==> building the synthetic recording"

# A pale page with a header bar. Three things happen on it:
#   0-8s    the page as it should look
#   8-14s   a red error banner appears, top right   (LOCALISED change, ~1.4% of
#           the screen -- the case a perceptual hash scores at zero)
#   14-24s  the whole page navigates to a confirmation screen (FULL-frame change)
#
# Between those, long stretches where nothing moves at all. That is the shape of
# a real walkthrough, and it is what makes the budget-is-a-ceiling behaviour
# visible: 24 seconds of video collapses to a handful of distinct pictures.
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=0xf4f4f6:s=1600x900:d=24:r=25" \
  -f lavfi -i "color=c=0x2b3a55:s=1600x120:d=24:r=25" \
  -f lavfi -i "color=c=0xffffff:s=900x520:d=24:r=25" \
  -f lavfi -i "color=c=0xd93a3a:s=360x50:d=24:r=25" \
  -f lavfi -i "color=c=0x1f7a4d:s=1600x900:d=24:r=25" \
  -f lavfi -i "color=c=0xffffff:s=700x300:d=24:r=25" \
  -filter_complex "\
    [0:v][1:v]overlay=x=0:y=0[a]; \
    [a][2:v]overlay=x=120:y=200[b]; \
    [b][3:v]overlay=x=1180:y=150:enable='between(t,8,14)'[c]; \
    [c][4:v]overlay=x=0:y=0:enable='gte(t,14)'[d]; \
    [d][5:v]overlay=x=450:y=300:enable='gte(t,14)'[v]" \
  -map "[v]" -c:v libx264 -pix_fmt yuv420p -t 24 "$VIDEO"

echo "==> probe (this is the cost gate; it writes nothing)"
python3 "$EXTRACT" probe "$VIDEO"

echo "==> extract, with the three cues the transcript pass returned"
# Cue timestamps are already offset by 1s: the narration lags what it describes.
rm -rf "$FRAMES"
python3 "$EXTRACT" extract "$VIDEO" \
  --out "$FRAMES" \
  --transcript "$HERE/checkout-walkthrough.transcript.srt" \
  --cues 9.0,15.5,20.0 \
  --effort average

echo "==> map the findings onto frames, BEFORE reading any of them"
python3 "$EXTRACT" map "$FRAMES" --findings "D1=9.0,D2=15.5,Q1=20.0"

echo
echo "Done. See report.md for what a model wrote from these frames,"
echo "and note how few distinct images it took to support every finding."
