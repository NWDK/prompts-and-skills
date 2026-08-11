#!/usr/bin/env python3
"""Select and extract the frames that matter from a local video.

  extract.py probe   VIDEO                      # metadata + frame budget + token cost
  extract.py extract VIDEO --out DIR [...]      # write frames + manifest.json

Claude cannot watch video. It reads images. So "letting Claude see a recording"
is really one question: WHICH frames, given a token budget you are paying for.

Two signals pick them, because in a screen recording visual change and
importance come apart. Scrolling a page changes almost every pixel and means
nothing; "and this bit is broken", said over a static screen, changes nothing
and is the most important frame in the file. So:

  - CUE frames come from the transcript (Claude picks the moment, the
    transcript supplies the timecode). They are reserved budget and are never
    dropped by deduplication.
  - FILL frames come from ffmpeg scene detection, deduplicated, topped up with
    uniform sampling. They are the safety net for anything done silently.

Everything is local. There is no network path in this file, by design: the
audio being transcribed is often someone narrating unreleased product over
screens showing real customer data.

Requires: ffmpeg, ffprobe, Pillow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:
    print("Pillow is required: python3 -m pip install Pillow", file=sys.stderr)
    raise SystemExit(2)


# --- constants ---------------------------------------------------------------

# PROVIDER-SPECIFIC (Claude). Images are billed in 28x28 patches, so token cost
# is a function of output pixels, not file size. Everything else in this file --
# frame selection, budgets, deduplication -- is provider-neutral; this constant
# and DEFAULT_LONG_EDGE below are the only two places a different vision API
# would need different numbers. See README.md for the verified limits.
PATCH = 28

# PROVIDER-SPECIFIC (Claude), and the only other one.
# Default long edge. 1568px is the standard-resolution tier's native maximum,
# so a 16:9 frame lands near 1560 visual tokens with no downscaling penalty, and
# it stays under the stricter per-image dimension cap that the API applies once
# a request carries more than 20 images. Raise to 2000 when you need to read
# small UI text; that is the ceiling before the many-image cap bites.
DEFAULT_LONG_EDGE = 1568
MAX_SAFE_LONG_EDGE = 2000

# Screen recordings change less per "scene" than filmed footage: a modal opening
# might move 15% of pixels where a hard cut moves 90%. 0.2 is tuned for screen
# content and is deliberately lower than a film default.
DEFAULT_SCENE_THRESHOLD = 0.2

# A spoken cue lands AFTER the thing it describes is already on screen. Grabbing
# the frame where the sentence ends catches the aftermath, not the subject.
DEFAULT_CUE_OFFSET = 1.0

# Two frames are "the same picture" when less than this fraction of it changed.
# Set by measurement, not feel: on a synthetic screen recording the noise floor
# between static frames was 0.000%, and the smallest change worth catching -- a
# 360x50 toast on a 1600x900 screen -- measured 2.20%. 0.5% sits in that gap
# with roughly 4x headroom under the smallest real signal. Recalibrate against
# real footage; anti-aliased text and a lossier encoder will raise the floor.
DEDUP_CHANGE = 0.005

# Frames are compared at this resolution, in RGB. Colour matters and greyscale
# hides it: a page whose hue changed but whose brightness did not measured 23%
# in greyscale against ~90% of the screen actually changing. In a UI that gap is
# the difference between a red error state and a green success one.
FINGERPRINT_SIZE = 64

# Per-pixel luminance difference (0-255) that counts as a real change rather
# than compression noise.
PIXEL_DELTA = 10

DEFAULT_MAX_FRAMES = 100

# Effort scales the FILL budget and how sensitive scene detection is. It never
# scales cues down: "small" means lean on the narration with a few visual
# references, not throw away the moments that were explicitly flagged.
EFFORT = {
    "small":   {"fill": 0.35, "scene_threshold": 0.30},
    "average": {"fill": 1.00, "scene_threshold": DEFAULT_SCENE_THRESHOLD},
    "large":   {"fill": 2.00, "scene_threshold": 0.12},
}
DEFAULT_EFFORT = "average"


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _require(binary):
    if shutil.which(binary) is None:
        die(f"{binary} is not installed. Install with: brew install ffmpeg")


def _unlink(path):
    try:
        os.remove(path)
    except OSError:
        pass


def _free_name(out_dir, name):
    """A filename no earlier pass is using.

    Frame names are derived from the timestamp, so a second pass over the same
    video regenerates identical names. Without this an --append run overwrites
    the frames the first pass wrote, and then drops them as already-covered,
    deleting images the existing manifest still points at.
    """
    base, ext = os.path.splitext(name)
    candidate, n = name, 2
    while os.path.exists(os.path.join(out_dir, candidate)):
        candidate = f"{base}_{n}{ext}"
        n += 1
    return candidate


# --- probe -------------------------------------------------------------------

def probe(video):
    """Real metadata from ffprobe. Never assert a duration from memory."""
    _require("ffprobe")
    if not os.path.exists(video):
        die(f"video not found: {video}")
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", video],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        die(f"ffprobe failed on {video}:\n{out.stderr.strip()}")
    d = json.loads(out.stdout)

    vs = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    if vs is None:
        die(f"no video stream in {video}")

    duration = float(d.get("format", {}).get("duration") or vs.get("duration") or 0)
    if duration <= 0:
        die(f"could not read a duration from {video}")

    return {
        "path": os.path.abspath(video),
        "bytes": os.path.getsize(video),
        "fingerprint": content_fingerprint(video),
        "duration": round(duration, 3),
        "width": int(vs.get("width") or 0),
        "height": int(vs.get("height") or 0),
        "fps": _parse_fps(vs.get("r_frame_rate")),
        "has_audio": any(s.get("codec_type") == "audio" for s in d.get("streams", [])),
    }


def content_fingerprint(path, chunk=1 << 20):
    """Size plus the first and last megabyte, hashed.

    Reading a multi-gigabyte recording end to end just to notice it changed
    would cost more than the extraction it protects, so this reads 2 MB and two
    seeks regardless of file size.

    It exists because metadata alone is NOT an identity, which a test caught
    rather than review: two four-second clips of different solid colours encode
    to byte-identical SIZES at the same duration and dimensions, so a
    metadata-only check waved through exactly the cross-source append it was
    added to prevent. Different content, same shape.
    """
    h = hashlib.sha256()
    size = os.path.getsize(path)
    h.update(str(size).encode())
    with open(path, "rb") as f:
        h.update(f.read(chunk))
        if size > chunk:
            f.seek(size - chunk)
            h.update(f.read(chunk))
    return h.hexdigest()


def source_identity(meta):
    """A stable identity for a recording, independent of where it sits.

    Path is deliberately NOT part of it: moving or renaming an unchanged file
    must not invalidate a manifest that points at it. The fingerprint carries
    the content; the metadata fields stay so that a manifest written before
    fingerprints existed can still be validated on what it does have.
    """
    return {k: meta.get(k)
            for k in ("fingerprint", "bytes", "duration", "width", "height")}


def assert_same_source(prior_source, meta, prior_path):
    """Refuse to merge frames from a different recording into one manifest.

    A manifest is an evidence record: every frame in it is attributed to the
    video named at its top. Appending a second video leaves the earlier frames
    filed under a recording they did not come from -- a document that looks
    correct and is wrong in the one way this tool exists to prevent. So this is
    a hard failure before anything is written, not a warning after.
    """
    if not prior_source:
        return
    # Compare only the keys the prior manifest actually carries, so a manifest
    # written before `bytes` existed still validates on its other fields.
    keys = [k for k, v in source_identity(prior_source).items() if v is not None]
    if keys and all(prior_source.get(k) == meta.get(k) for k in keys):
        return
    die(
        f"this output directory already holds frames from a different recording.\n"
        f"  existing: {os.path.basename(prior_source.get('path') or '?')}  "
        f"({prior_source.get('duration')}s, {prior_source.get('width')}x{prior_source.get('height')})\n"
        f"  new:      {os.path.basename(meta['path'])}  "
        f"({meta['duration']}s, {meta['width']}x{meta['height']})\n"
        f"  manifest: {prior_path}\n"
        f"  Appending would file the existing frames under the wrong video. Use a\n"
        f"  separate --out directory for this recording. If the source really is the\n"
        f"  same file and was re-encoded, start a fresh run instead of appending."
    )


def _parse_fps(rate):
    if not rate or "/" not in str(rate):
        return None
    num, den = str(rate).split("/", 1)
    try:
        num, den = float(num), float(den)
    except ValueError:
        return None
    return round(num / den, 3) if den else None


# --- budget ------------------------------------------------------------------

def resolve_max_frames(explicit, effort):
    """The hard ceiling on frames, which effort has to move or it does nothing.

    An explicit --max-frames is the caller's own cap and is respected as given.
    Otherwise the ceiling scales with effort, because the tier table already
    reaches the default cap on any recording over ten minutes: clamping an
    effort-scaled target to a fixed ceiling made `large` silently identical to
    `average` on exactly the long recordings where more detail was being asked
    for. Spend is gated by `probe` showing the cost, not by this number.
    """
    if explicit is not None:
        return max(1, explicit)
    return max(1, int(round(DEFAULT_MAX_FRAMES * EFFORT[effort]["fill"])))


def plan_budget(duration, max_frames=DEFAULT_MAX_FRAMES, focus=False,
                effort=DEFAULT_EFFORT):
    """Target a frame COUNT, not a capture rate.

    Frame count is what costs money, so it is what gets capped. Deriving the
    rate from the duration means a long recording is automatically sampled more
    sparsely instead of blowing the budget, and you never have to guess a
    sensible fps up front.

    `focus=True` is the denser tier used when the caller names a time range:
    asking about 0:45-0:50 means zooming in, and wanting detail there.
    """
    if duration <= 0:
        return 1
    if focus:
        if duration <= 5:
            target = max(10, int(round(duration * 6)))
        elif duration <= 15:
            target = max(30, int(round(duration * 4)))
        elif duration <= 30:
            target = 60
        elif duration <= 60:
            target = 80
        else:
            target = DEFAULT_MAX_FRAMES
    else:
        if duration <= 30:
            target = max(12, int(round(duration)))
        elif duration <= 60:
            target = 40
        elif duration <= 180:
            target = 60
        elif duration <= 600:
            target = 80
        else:
            target = DEFAULT_MAX_FRAMES
    target = int(round(target * EFFORT[effort]["fill"]))
    return max(1, min(max_frames, target))


def output_dims(width, height, long_edge):
    """Scale to fit `long_edge` on the longer side, preserving aspect ratio."""
    if not width or not height:
        return long_edge, long_edge
    if max(width, height) <= long_edge:
        return width, height
    scale = long_edge / float(max(width, height))
    # Even dimensions keep every encoder happy.
    w = max(2, int(round(width * scale)) // 2 * 2)
    h = max(2, int(round(height * scale)) // 2 * 2)
    return w, h


def visual_tokens(width, height):
    """Claude's image cost: ceil(w/28) * ceil(h/28) patches."""
    return math.ceil(width / PATCH) * math.ceil(height / PATCH)


def cost_report(meta, target, long_edge):
    w, h = output_dims(meta["width"], meta["height"], long_edge)
    per = visual_tokens(w, h)
    return {
        "output_width": w,
        "output_height": h,
        "tokens_per_frame": per,
        "frames": target,
        "estimated_visual_tokens": per * target,
    }


# --- transcript --------------------------------------------------------------
# Both whisper.cpp JSON and .srt are accepted, so any tool in the pipeline can
# agree on what a transcript is. The dependency runs skill -> tool, never the
# reverse: this file knows nothing about who is calling it.

def load_transcript(path):
    """Load a transcript into a list of {text, start, end} items."""
    if not os.path.exists(path):
        die(f"transcript not found: {path}")
    low = path.lower()
    if low.endswith(".json"):
        return _segments_from_whisper_json(path)
    if low.endswith(".srt"):
        return _items_from_srt(path)
    die(f"unsupported transcript format (need .json or .srt): {path}")


def _segments_from_whisper_json(path):
    """whisper.cpp full JSON, at segment level.

    Word-level timing exists in the same file and is what you would want to
    resolve a quote to exact in/out points. Here we only ever need "what was
    being said around this timestamp", so segments are the right grain and
    much cheaper.
    """
    with open(path, encoding="utf-8", errors="replace") as f:
        d = json.load(f)
    items = []
    for seg in d.get("transcription", []):
        off = seg.get("offsets", {}) or {}
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        items.append({
            "text": text,
            "start": off.get("from", 0) / 1000.0,
            "end": off.get("to", 0) / 1000.0,
        })
    return items


def _items_from_srt(path):
    """Parse an .srt into segment-level {text, start, end} items."""
    ts = re.compile(r"(\d\d):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d\d):(\d\d):(\d\d)[,.](\d{3})")
    with open(path, encoding="utf-8", errors="replace") as f:
        blocks = re.split(r"\n\s*\n", f.read().strip())
    items = []
    for b in blocks:
        lines = b.splitlines()
        for i, ln in enumerate(lines):
            m = ts.match(ln.strip())
            if m:
                g = list(map(int, m.groups()))
                items.append({
                    "text": " ".join(lines[i + 1:]).strip(),
                    "start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0,
                    "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0,
                })
                break
    return items


def spoken_at(items, t):
    """The transcript line being spoken over timestamp `t`, if any."""
    for it in items:
        if it["start"] <= t <= it["end"]:
            return it["text"]
    # Nothing spoken exactly here: fall back to the nearest line within 2s so a
    # frame grabbed just before a sentence still carries its context.
    best, best_gap = None, 2.0
    for it in items:
        gap = min(abs(it["start"] - t), abs(it["end"] - t))
        if gap < best_gap:
            best, best_gap = it["text"], gap
    return best


def find_marker_cues(items, keywords, offset):
    """Timestamps for explicit spoken markers, e.g. saying 'screenshot' out loud.

    Additive only: the semantic pass does the real work and nobody should have
    to narrate unnaturally to get a good result. This is the override for when
    you know in the moment that something matters.
    """
    if not keywords:
        return []
    pattern = re.compile("|".join(re.escape(k.lower()) for k in keywords))
    hits = []
    for it in items:
        if pattern.search(it["text"].lower()):
            hits.append(max(0.0, it["start"] - offset))
    return sorted(set(round(t, 2) for t in hits))


# --- extraction --------------------------------------------------------------

def _scale_filter(w, h):
    return f"scale={w}:{h}:flags=lanczos"


def extract_at_timestamps(video, timestamps, out_dir, w, h, kind="cue"):
    """One frame per timestamp. Used for cues, which must land exactly.

    `-ss` before `-i` seeks fast AND accurately on a seekable file (ffmpeg
    decodes from the preceding keyframe and discards), so this is both cheap
    and correct.
    """
    _require("ffmpeg")
    frames = []
    for t in timestamps:
        name = _free_name(out_dir, f"{kind}_t{t:08.2f}.jpg")
        dest = os.path.join(out_dir, name)
        r = subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-ss", f"{t:.3f}", "-i", video,
             "-frames:v", "1", "-vf", _scale_filter(w, h), "-q:v", "2", dest],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not os.path.exists(dest):
            print(f"  warn: no frame at {t:.2f}s ({r.stderr.strip()[:80]})", file=sys.stderr)
            continue
        # Dimensions travel WITH the frame. A later pass may use a different
        # --resolution, and a collection-level figure would then describe some of
        # its own contents incorrectly while looking authoritative.
        frames.append({"timestamp": round(t, 2), "reason": kind, "file": name,
                       "width": w, "height": h, "tokens": visual_tokens(w, h)})
    return frames


def detect_scene_frames(video, out_dir, w, h, threshold, start=None, end=None):
    """Single decode pass: emit a frame wherever the picture materially changes.

    One pass writes the jpgs and reports their timestamps via showinfo, rather
    than detecting in one pass and re-decoding to extract in another.
    """
    _require("ffmpeg")
    tmp = os.path.join(out_dir, "_scene")
    os.makedirs(tmp, exist_ok=True)

    cmd = ["ffmpeg", "-hide_banner", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}"]
    if end is not None:
        cmd += ["-to", f"{end:.3f}"]
    cmd += [
        "-i", video,
        # eq(n,0) keeps the very first frame so a static recording still yields
        # something rather than an empty set.
        "-vf", rf"select='eq(n\,0)+gt(scene\,{threshold})',{_scale_filter(w, h)},showinfo",
        "-vsync", "vfr", "-q:v", "2",
        os.path.join(tmp, "s_%05d.jpg"),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die(f"ffmpeg scene pass failed:\n{r.stderr.strip()[-400:]}")

    times = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]
    files = sorted(f for f in os.listdir(tmp) if f.endswith(".jpg"))

    offset = start or 0.0
    frames = []
    for i, fn in enumerate(files):
        t = (times[i] + offset) if i < len(times) else offset
        name = _free_name(out_dir, f"scene_t{t:08.2f}.jpg")
        os.replace(os.path.join(tmp, fn), os.path.join(out_dir, name))
        frames.append({"timestamp": round(t, 2), "reason": "scene", "file": name,
                       "width": w, "height": h, "tokens": visual_tokens(w, h)})
    shutil.rmtree(tmp, ignore_errors=True)
    return frames


def extract_uniform(video, out_dir, w, h, count, duration, start=0.0):
    """Evenly spaced frames. The top-up when scene detection finds too little."""
    if count <= 0 or duration <= 0:
        return []
    step = duration / (count + 1)
    times = [round(start + step * (i + 1), 2) for i in range(count)]
    return extract_at_timestamps(video, times, out_dir, w, h, kind="fill")


# --- deduplication -----------------------------------------------------------

def fingerprint(path, size=FINGERPRINT_SIZE):
    """Downscaled RGB pixels. Comparison is per-pixel, not a global hash."""
    with Image.open(path) as im:
        # mode "RGB" is three bytes per pixel, row-major
        return im.convert("RGB").resize((size, size), Image.LANCZOS).tobytes()


def changed_fraction(a, b, pixel_delta=PIXEL_DELTA):
    """How much of the picture materially changed, 0.0 to 1.0.

    A global perceptual hash (dHash, aHash) is the wrong instrument for screen
    recordings and was the first thing tried here. It reduces the whole frame to
    a coarse gradient signature, so a change confined to one region leaves that
    signature untouched: measured on real content, frames with an obviously
    different panel scored a dHash distance of ZERO and were dropped as
    duplicates. A dropdown opening, an error banner appearing, a field turning
    red -- exactly the frames worth keeping -- are all localised changes.

    Counting pixels that actually differ keeps localised change visible, at the
    cost of being blind to very small text edits. Cues cover those: if it
    mattered enough to say out loud, it does not need the visual pass to notice.
    """
    if len(a) != len(b) or not a:
        return 1.0
    changed = 0
    for i in range(0, len(a), 3):
        if (abs(a[i] - b[i]) > pixel_delta
                or abs(a[i + 1] - b[i + 1]) > pixel_delta
                or abs(a[i + 2] - b[i + 2]) > pixel_delta):
            changed += 1
    return changed / (len(a) // 3)


def dedupe(frames, out_dir, min_change=DEDUP_CHANGE):
    """Drop frames that look the same as the one kept before them."""
    kept, dropped, last = [], [], None
    for f in frames:
        p = os.path.join(out_dir, f["file"])
        if not os.path.exists(p):
            continue
        try:
            fp = fingerprint(p)
        except Exception:
            kept.append(f)
            continue
        if last is not None and changed_fraction(fp, last) < min_change:
            dropped.append(f)
            continue
        last = fp
        kept.append(f)
    for f in dropped:
        _unlink(os.path.join(out_dir, f["file"]))
    return kept, len(dropped)


def collapse_identical(frames, out_dir, min_change=DEDUP_CHANGE):
    """Point entries at one shared image where the picture is the same.

    Cue entries are never dropped: the flagged moment and the line spoken over
    it are the whole point of a cue. But there is no reason to pay for the same
    pixels twice, and a cue raised over a screen that has not changed since the
    last frame is the common case, not the exception. So identical pictures
    collapse to a single file and the extra entries reference it, which leaves
    both kinds of consumer correct: one that reads the manifest sends each
    distinct image once, and one that simply globs the folder gets the same set.

    Decide per FILE and then remap every entry, rather than deciding per entry.
    Several entries can already point at one file from an earlier pass; collapsing
    that file on the first entry's behalf would unlink it out from under the rest,
    leaving them referencing a path that no longer exists.
    """
    order = []
    for f in frames:
        if f["file"] not in order:
            order.append(f["file"])

    canonical, seen = {}, []
    for name in order:
        path = os.path.join(out_dir, name)
        if not os.path.exists(path):
            continue
        try:
            fp = fingerprint(path)
        except Exception:
            canonical[name] = name
            seen.append((None, name))
            continue
        match = next((n for prev, n in seen
                      if prev is not None and changed_fraction(fp, prev) < min_change), None)
        if match:
            canonical[name] = match
            _unlink(path)
        else:
            canonical[name] = name
            seen.append((fp, name))

    collapsed = 0
    for f in frames:
        target = canonical.get(f["file"], f["file"])
        if target != f["file"]:
            f["shares_image_with"] = target
            f["file"] = target
            collapsed += 1
    return collapsed


def midpoints(timestamps, minimum_gap=1.0):
    """Halfway between each pair of frames we already have.

    The second-pass move: when a first sweep turned out too sparse, the useful
    next samples are the ones between what you already looked at, not a re-run
    from scratch at a higher budget.
    """
    ts = sorted(set(timestamps))
    return [round((a + b) / 2, 2) for a, b in zip(ts, ts[1:]) if (b - a) >= minimum_gap]


def even_sample(items, k):
    """Reduce to k items, always keeping the first and last."""
    if k <= 0:
        return []
    if len(items) <= k:
        return items
    if k == 1:
        return [items[0]]
    step = (len(items) - 1) / (k - 1)
    return [items[int(round(i * step))] for i in range(k)]


# --- commands ----------------------------------------------------------------

def cmd_probe(args):
    meta = probe(args.video)
    focus = args.start is not None or args.end is not None
    span = _span(meta, args.start, args.end)
    max_frames = resolve_max_frames(args.max_frames, args.effort)
    target = plan_budget(span, max_frames, focus=focus, effort=args.effort)
    cost = cost_report(meta, target, args.resolution)

    if args.json:
        print(json.dumps({"source": meta, "effort": args.effort,
                          "budget": target, **cost}, indent=2))
        return

    print(f"\n{os.path.basename(meta['path'])}")
    print(f"  duration     {meta['duration']:.1f}s"
          + (f"  (window {span:.1f}s)" if focus else ""))
    print(f"  source       {meta['width']}x{meta['height']}"
          + (f" @ {meta['fps']}fps" if meta["fps"] else "")
          + ("  + audio" if meta["has_audio"] else "  (no audio)"))
    print(f"  output       {cost['output_width']}x{cost['output_height']}"
          f"  ({cost['tokens_per_frame']:,} visual tokens/frame)")
    print(f"  frame budget {target}   ({args.effort} effort; "
          + ", ".join(
              f"{name}={plan_budget(span, resolve_max_frames(args.max_frames, name), focus, name)}"
              for name in EFFORT if name != args.effort) + ")")
    print(f"  ESTIMATE     ~{cost['estimated_visual_tokens']:,} visual tokens\n")


def _span(meta, start, end):
    s = start or 0.0
    e = end if end is not None else meta["duration"]
    return max(0.0, min(e, meta["duration"]) - s)


def _mmss(seconds):
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"


def capture_time(frames, filename):
    """When the image was actually taken, as opposed to when a finding cites it.

    An entry that shares another entry's image carries the citing timestamp, not
    the picture's. The owning entry is the one not pointing elsewhere.
    """
    owners = [f for f in frames
              if f["file"] == filename and "shares_image_with" not in f]
    if owners:
        return owners[0]["timestamp"]
    m = re.search(r"_t(\d+\.\d+)", filename)
    return float(m.group(1)) if m else None


def cmd_map(args):
    """Map findings to the frames that support them.

    Any document that cites findings needs this, and doing it by hand invites two
    mistakes. It over-attaches, because several findings routinely share one
    image and the naive count is the finding count. And it misreports the
    picture, because a shared image was captured at the earlier moment the screen
    last changed, not at the second the finding cites -- correct, but confusing
    in a report unless it is said out loud.
    """
    mpath = os.path.join(args.frames_dir, "manifest.json")
    if not os.path.exists(mpath):
        die(f"no manifest at {mpath}")
    with open(mpath) as f:
        frames = json.load(f).get("frames", [])
    if not frames:
        die(f"manifest at {mpath} lists no frames")

    findings = _parse_findings(args)
    if not findings:
        die("give findings via --findings (id=seconds,...) or a .json file, or --cues")

    rows, by_file = [], {}
    for fid, t in findings:
        hit = min(frames, key=lambda x: abs(x["timestamp"] - t))
        cap = capture_time(frames, hit["file"])
        rows.append({"id": fid, "cited_at": round(t, 2), "file": hit["file"],
                     "captured_at": cap,
                     "spoken": hit.get("spoken")})
        by_file.setdefault(hit["file"], []).append(fid)

    for r in rows:
        r["shared_with"] = [o for o in by_file[r["file"]] if o != r["id"]]
        r["captured_elsewhere"] = (r["captured_at"] is not None
                                   and abs(r["captured_at"] - r["cited_at"]) > 2)

    if args.json:
        print(json.dumps({"findings": len(rows), "distinct_images": len(by_file),
                          "rows": rows}, indent=2))
        return

    drift = sum(1 for r in rows if r["captured_elsewhere"])
    shared = sum(1 for v in by_file.values() if len(v) > 1)
    print(f"\n**{len(by_file)} images cover all {len(rows)} findings.** "
          f"Attach those, not every frame in the folder.\n")
    if drift:
        print(f"- **The filename is the capture time, not the finding time.** "
              f"{drift} of {len(rows)} findings are supported by an image captured "
              f"earlier, because the screen had not changed and identical pictures "
              f"collapse to one file. Still the right image; not that exact second.")
    if shared:
        print(f"- **{shared} images serve more than one finding.** Attach once and "
              f"reference from both, or the report doubles up.")
    print("\n| Finding | Cited at | Frame file | Note |\n|---|---|---|---|")
    for r in rows:
        notes = []
        if r["captured_elsewhere"]:
            notes.append(f"image captured {_mmss(r['captured_at'])} — screen unchanged since")
        if r["shared_with"]:
            notes.append("also serves " + ", ".join(r["shared_with"]))
        print(f"| {r['id']} | {_mmss(r['cited_at'])} | `{r['file']}` | "
              f"{'; '.join(notes) or '—'} |")
    print()


def _parse_findings(args):
    """Accept id=seconds pairs, a JSON file, or bare timestamps."""
    if args.findings and args.findings.lower().endswith(".json"):
        if not os.path.exists(args.findings):
            die(f"findings file not found: {args.findings}")
        with open(args.findings) as f:
            data = json.load(f)
        return [(str(d.get("id") or i + 1), float(d["t"])) for i, d in enumerate(data)]
    if args.findings:
        out = []
        for tok in args.findings.replace(",", " ").split():
            if "=" not in tok:
                die(f"expected id=seconds, got {tok!r}")
            fid, _, val = tok.partition("=")
            try:
                out.append((fid, float(val)))
            except ValueError:
                die(f"not a timestamp in seconds: {val!r}")
        return out
    return [(str(i + 1), t) for i, t in enumerate(args.cues or [])]


def cmd_extract(args):
    meta = probe(args.video)
    focus = args.start is not None or args.end is not None
    span = _span(meta, args.start, args.end)
    max_frames = resolve_max_frames(args.max_frames, args.effort)
    target = plan_budget(span, max_frames, focus=focus, effort=args.effort)
    w, h = output_dims(meta["width"], meta["height"], args.resolution)
    per_frame = visual_tokens(w, h)
    threshold = (args.scene_threshold if args.scene_threshold is not None
                 else EFFORT[args.effort]["scene_threshold"])

    if args.resolution > MAX_SAFE_LONG_EDGE:
        print(f"  warn: long edge {args.resolution} exceeds {MAX_SAFE_LONG_EDGE}; requests "
              f"carrying more than 20 images may be rejected", file=sys.stderr)

    # NOT created yet. Two paths below exit without writing anything -- a dry run,
    # and the refusal when explicit --max-frames cannot hold the cues -- and both
    # promise exactly that. Creating the directory first made both of them leave a
    # trace, which is a small lie in the one place this tool asks to be trusted.
    # It is created immediately before the first frame is written.
    out_dir = args.out

    # --- a prior run: --append and --refine build on it rather than replace it ---
    #
    # `--out` is a user-supplied directory that may hold anything. Ownership is
    # therefore TRACKED, never inferred: a file is ours only if a prior manifest
    # recorded it or this run created it. Matching on the filename pattern was
    # not enough -- it silently claimed any image that happened to look like our
    # output, and the final consistency sweep then deleted whatever it did not
    # recognise. Nothing here removes a file this tool cannot prove it wrote.
    prior, prior_path = [], os.path.join(out_dir, "manifest.json")
    prior_doc = {}
    if os.path.exists(prior_path):
        try:
            with open(prior_path) as f:
                prior_doc = json.load(f)
        except (json.JSONDecodeError, OSError):
            prior_doc = {}          # unreadable manifest owns nothing
    owned = {f["file"] for f in prior_doc.get("frames", []) if f.get("file")}

    appending = args.append or args.refine
    if appending:
        if not prior_doc:
            die(f"--{'refine' if args.refine else 'append'} needs an existing "
                f"manifest at {prior_path}")
        assert_same_source(prior_doc.get("source"), meta, prior_path)
        prior = [p for p in prior_doc.get("frames", [])
                 if os.path.exists(os.path.join(out_dir, p["file"]))]
    else:
        # Fresh run: clear only what a prior pass of this tool recorded.
        for stale in owned:
            _unlink(os.path.join(out_dir, stale))

    items = load_transcript(args.transcript) if args.transcript else []

    # --- cues: reserved budget, extracted first, never deduplicated ---
    cues = list(args.cues or [])
    if items and args.marker:
        cues += find_marker_cues(items, args.marker, args.cue_offset)
    if args.refine:
        cues += midpoints([p["timestamp"] for p in prior])
    cues = sorted({round(max(0.0, c), 2) for c in cues})
    if args.start is not None:
        cues = [c for c in cues if c >= args.start]
    if args.end is not None:
        cues = [c for c in cues if c <= args.end]
    # Don't re-extract a moment the prior pass already covered.
    if prior:
        have = [p["timestamp"] for p in prior]
        cues = [c for c in cues if all(abs(c - t) > 0.5 for t in have)]

    # Effort scales the visual sweep, never the flagged moments. A cue is the
    # caller saying "this moment matters"; dropping one can remove the only
    # evidence for a finding while the run still reports success.
    #
    # So the two ceilings are NOT the same thing, and conflating them was the
    # bug here. An effort tier's cap is OUR planning default and must grow to
    # fit the cues. An explicit --max-frames is the CALLER's limit, and when it
    # cannot hold the cues the honest move is to stop and say so rather than
    # choose on their behalf which of their cues to throw away.
    if len(cues) + len(prior) > max_frames:
        if args.max_frames is not None:
            die(f"{len(cues)} cues"
                + (f" plus {len(prior)} frames already in {out_dir}" if prior else "")
                + f" exceed your --max-frames {args.max_frames}.\n"
                f"  Refusing to choose which of your cues to discard. Either raise the\n"
                f"  cap (--max-frames {len(cues) + len(prior)}) or split the run into\n"
                f"  sections with --start/--end.")
        max_frames = len(cues) + len(prior)
        print(f"  note: {len(cues)} cues exceed the {args.effort} tier's default "
              f"ceiling; raising it to {max_frames} to keep every cue")
    if len(cues) > target:
        target = min(max_frames, len(cues) + len(prior))

    label = f"{args.effort} effort" + (", refine pass" if args.refine
                                       else ", appending" if args.append else "")
    print(f"\n  budget {target} frames  ({label}; {per_frame:,} tokens each, "
          f"~{per_frame * target:,} total)")
    if prior:
        print(f"  prior  {len(prior)} frames already in {out_dir}")
    if args.dry_run:
        print(f"  cues   {len(cues)}\n  dry run, nothing written\n")
        return

    # First write of the run. Everything above this line is read-only.
    os.makedirs(out_dir, exist_ok=True)

    cue_frames = extract_at_timestamps(args.video, cues, out_dir, w, h, kind="cue") if cues else []
    owned |= {f["file"] for f in cue_frames}
    print(f"  cues   {len(cue_frames)} pinned")

    # --- fill: scene detection, topped up if thin, then deduplicated ---
    #
    # The budget is a CEILING, not a quota. A recording that sits on one static
    # screen should yield a handful of frames, not a padded thirty: paying to
    # show Claude the same picture twenty times is the exact waste this tool
    # exists to avoid. So the uniform top-up happens BEFORE deduplication and
    # coming in under budget is a correct outcome, not a shortfall to fix.
    # A refine pass is deliberately cues-only: it fills the gaps between frames
    # you already have, rather than re-running the sweep you already paid for.
    remaining = 0 if args.refine else max(0, target - len(cue_frames) - len(prior))
    fill_frames, dropped = [], 0
    if remaining:
        candidates = detect_scene_frames(args.video, out_dir, w, h,
                                         threshold, args.start, args.end)
        short = remaining - len(candidates)
        if short > 0:
            candidates += extract_uniform(args.video, out_dir, w, h, short,
                                          span, args.start or 0.0)
        owned |= {f["file"] for f in candidates}
        # A cue or a prior frame already covers its moment; drop fill landing there.
        covered = cue_frames + prior
        keep_c = []
        for f in candidates:
            if any(abs(f["timestamp"] - c["timestamp"]) <= 1.0 for c in covered):
                _unlink(os.path.join(out_dir, f["file"]))
            else:
                keep_c.append(f)
        candidates = sorted(keep_c, key=lambda f: f["timestamp"])
        candidates, dropped = dedupe(candidates, out_dir, args.dedup_change)
        if len(candidates) > remaining:
            keep = {id(f) for f in even_sample(candidates, remaining)}
            for f in candidates:
                if id(f) not in keep:
                    _unlink(os.path.join(out_dir, f["file"]))
            candidates = [f for f in candidates if id(f) in keep]
        fill_frames = candidates
    print(f"  fill   {len(fill_frames)} kept ({dropped} near-duplicates dropped)")

    # --- merge, label, manifest ---
    frames = sorted(prior + cue_frames + fill_frames, key=lambda f: f["timestamp"])
    collapsed = collapse_identical(frames, out_dir, args.dedup_change)
    for i, f in enumerate(frames):
        f["index"] = i
        if items:
            f["spoken"] = spoken_at(items, f["timestamp"])

    # Backfill dimensions on frames carried from a manifest written before they
    # were recorded per-frame. That older manifest had one collection-level figure
    # and it was correct for everything it held, so it is the right source here.
    old = prior_doc.get("output") or {}
    for f in frames:
        if "tokens" not in f and old.get("tokens_per_frame"):
            f["width"], f["height"] = old.get("width"), old.get("height")
            f["tokens"] = old["tokens_per_frame"]

    # Cost follows distinct IMAGES, not entries: several entries can annotate
    # the same unchanged screen at different moments. And it is summed from what
    # each frame ACTUALLY is, because a pass at a different --resolution leaves a
    # collection with more than one frame size in it -- which the documented
    # "go back at a higher resolution" workflow does on purpose.
    seen_files, actual_tokens = set(), 0
    for f in frames:
        if f["file"] not in seen_files:
            seen_files.add(f["file"])
            actual_tokens += f.get("tokens") or per_frame
    distinct = len(seen_files)
    sizes = {(f.get("width"), f.get("height")) for f in frames if f.get("width")}
    if collapsed:
        print(f"  shared {collapsed} entr{'y' if collapsed == 1 else 'ies'} "
              f"reuse an identical image")

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": meta,
        "window": {"start": args.start, "end": args.end} if focus else None,
        # THIS PASS's settings, not a description of the whole collection. Every
        # frame carries its own width/height/tokens; read those, not this, when
        # you need to know what an image actually is.
        "output": {"long_edge": args.resolution, "width": w, "height": h,
                   "tokens_per_frame": per_frame,
                   "applies_to": "frames written by this pass",
                   "collection_is_mixed_resolution": len(sizes) > 1},
        # THIS PASS again, same as `output` above.
        "budget": {"target": target, "effort": args.effort,
                   "scene_threshold": threshold, "dedup_change": args.dedup_change,
                   "carried_from_prior_pass": len(prior),
                   "cues": len(cue_frames), "fill": len(fill_frames),
                   "duplicates_dropped": dropped,
                   "entries_sharing_an_image": collapsed,
                   "applies_to": "frames written by this pass"},

        # The collection's actual history. Selection settings decide how hard the
        # sweep looked, so a reader inferring coverage from a single figure would
        # be wrong about every frame an earlier pass contributed -- and coverage
        # is exactly what someone asks a manifest.
        #
        # Recorded rather than refused. Refusing an append whose settings differ
        # sounds tidier and is worse: --effort DEFAULTS to "average", so a first
        # pass at --effort small followed by the documented targeted re-fetch
        # (--append --cues 214.0, no effort given) would be rejected over a value
        # the caller never typed.
        "passes": (prior_doc.get("passes") or []) + [{
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mode": "refine" if args.refine else "append" if args.append else "fresh",
            "effort": args.effort,
            "scene_threshold": threshold,
            "dedup_change": args.dedup_change,
            "long_edge": args.resolution,
            "cues": len(cue_frames),
            "fill": len(fill_frames),
        }],
        # An append that omits --transcript is not a statement that no transcript
        # was used; it just did not need one for this pass. Blanking the field
        # would erase the provenance of every frame the earlier pass labelled.
        "transcript": (os.path.abspath(args.transcript) if args.transcript
                       else prior_doc.get("transcript")),
        "distinct_images": distinct,
        "estimated_visual_tokens": actual_tokens,
        "frames": frames,
    }
    mpath = os.path.join(out_dir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)

    # The manifest is the contract. A stray jpg left behind by a filter would be
    # silently fed to the model by anything that globs the folder, so assert the
    # two agree rather than trusting that every drop path also unlinked.
    #
    # But this sweep only ever acts on files this tool can PROVE it wrote. An
    # image it does not recognise belongs to whoever put it there: report it and
    # leave it. Deleting on non-recognition made a shared output directory
    # destructive to its other contents, which is never an acceptable cost for
    # keeping our own bookkeeping tidy.
    on_disk = {p for p in os.listdir(out_dir) if p.endswith(".jpg")}
    listed = {f["file"] for f in frames}
    stale_ours = (on_disk & owned) - listed
    for orphan in stale_ours:
        _unlink(os.path.join(out_dir, orphan))
    if stale_ours:
        print(f"  note: removed {len(stale_ours)} frame(s) this tool wrote that are "
              f"not in the manifest", file=sys.stderr)
    unknown = sorted(on_disk - owned - listed)
    if unknown:
        print(f"  warn: {len(unknown)} image(s) in {out_dir} were not written by this "
              f"tool and have been left alone: {', '.join(unknown[:3])}"
              + (" ..." if len(unknown) > 3 else "")
              + "\n        A consumer that globs this folder will pick them up. Prefer a "
                "directory\n        used only for this run, or read manifest.json rather "
                "than the folder.", file=sys.stderr)
    missing = listed - on_disk
    if missing:
        # An entry pointing at a file that is gone would be silently skipped by a
        # consumer, so fail loudly rather than ship a manifest that lies.
        die(f"manifest references {len(missing)} missing frame(s): "
            f"{sorted(missing)[:3]}. This is a bug in the extractor.")

    actual = actual_tokens
    n = len(frames)
    print(f"\n  {n} frame{'' if n == 1 else 's'} "
          f"({distinct} distinct image{'' if distinct == 1 else 's'}) -> {out_dir}")
    print(f"  ACTUAL ~{actual:,} visual tokens", end="")
    if distinct < target:
        # Under budget is the good outcome on a static recording. Say so, or it
        # reads as a shortfall and someone "fixes" it by padding the budget.
        print(f"  ({target - distinct} under budget, "
              f"~{per_frame * (target - distinct):,} tokens saved)")
    else:
        print()
    print(f"  manifest: {mpath}\n")


# --- cli ---------------------------------------------------------------------

def _timestamps(value):
    out = []
    for tok in str(value).replace(",", " ").split():
        try:
            out.append(float(tok))
        except ValueError:
            die(f"not a timestamp in seconds: {tok!r}")
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Select and extract the frames that matter from a local video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    def shared(p):
        p.add_argument("video")
        p.add_argument("--effort", choices=list(EFFORT), default=DEFAULT_EFFORT,
                       help="how hard to sweep visually: small leans on the narration "
                            "with a few visual references, large samples densely "
                            f"(default {DEFAULT_EFFORT}). Never reduces cues.")
        p.add_argument("--max-frames", type=int, default=None,
                       help=f"hard cap on frames. Unset, the ceiling follows effort "
                            f"(small {int(DEFAULT_MAX_FRAMES * EFFORT['small']['fill'])}, "
                            f"average {DEFAULT_MAX_FRAMES}, "
                            f"large {int(DEFAULT_MAX_FRAMES * EFFORT['large']['fill'])}). "
                            f"Set it and your number wins for every effort.")
        p.add_argument("--resolution", type=int, default=DEFAULT_LONG_EDGE,
                       help=f"output long edge in px (default {DEFAULT_LONG_EDGE}; "
                            f"{MAX_SAFE_LONG_EDGE} is the many-image ceiling)")
        p.add_argument("--start", type=float, help="window start in seconds")
        p.add_argument("--end", type=float, help="window end in seconds")

    pp = sub.add_parser("probe", help="metadata, frame budget and token cost; writes nothing")
    shared(pp)
    pp.add_argument("--json", action="store_true")
    pp.set_defaults(func=cmd_probe)

    pe = sub.add_parser("extract", help="write frames + manifest.json")
    shared(pe)
    pe.add_argument("--out", required=True, help="output directory")
    pe.add_argument("--transcript", help="whisper .json or .srt; labels frames and enables --marker")
    pe.add_argument("--cues", type=_timestamps, default=[],
                    help="cue timestamps in seconds, comma or space separated. Taken "
                         "ABSOLUTELY -- --cue-offset is not applied. A caller deriving "
                         "these from a transcript should subtract the offset itself, "
                         "since a spoken reference lags the thing it describes.")
    pe.add_argument("--marker", action="append", default=[],
                    help="spoken keyword that pins a frame (repeatable), e.g. --marker screenshot")
    pe.add_argument("--cue-offset", type=float, default=DEFAULT_CUE_OFFSET,
                    help=f"seconds to rewind a --marker cue (default {DEFAULT_CUE_OFFSET}). "
                         "Applies to --marker only; --cues and --refine are absolute.")
    pe.add_argument("--scene-threshold", type=float, default=None,
                    help="0-1 scene sensitivity; overrides the effort tier's value "
                         f"(average uses {DEFAULT_SCENE_THRESHOLD}, tuned for screen recordings)")
    pe.add_argument("--append", action="store_true",
                    help="add to an existing output dir and merge into its manifest, "
                         "instead of replacing it")
    pe.add_argument("--refine", action="store_true",
                    help="second pass: sample halfway between the frames already in the "
                         "manifest and append them. Implies --append; runs no scene sweep.")
    pe.add_argument("--dedup-change", type=float, default=DEDUP_CHANGE,
                    help="fraction of the picture that must change to count as a new "
                         f"frame (default {DEDUP_CHANGE}, i.e. {DEDUP_CHANGE * 100:.1f} "
                         "percent). Lower it if near-identical screens are being kept; "
                         "raise it if changes you care about are being dropped.")
    pe.add_argument("--dry-run", action="store_true", help="print the cost estimate and stop")
    pe.set_defaults(func=cmd_extract)

    pm = sub.add_parser("map", help="map findings to the frames that support them")
    pm.add_argument("frames_dir", help="a directory containing manifest.json")
    pm.add_argument("--findings", help="'D1=71.8,D2=95.6' or a .json file of {id,t}")
    pm.add_argument("--cues", type=_timestamps, default=[],
                    help="bare timestamps, auto-numbered, when you have no finding ids")
    pm.add_argument("--json", action="store_true")
    pm.set_defaults(func=cmd_map)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
