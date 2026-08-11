# Video Frames

Selects and extracts the frames that matter from a **local** video, so Claude can see what happened on screen.

Claude has no native video input — the API takes images, not video. So this is the step that decides *which* frames are worth paying for, and hands them over labelled with what was being said at that moment.

**No network path exists in this tool, by design.** Walkthrough audio is often someone narrating unreleased product over screens showing real customer data, so transcription stays local too (see [`tools/transcription/`](../transcription/)) and nothing leaves the machine.

Driven by [`skills/video-review/`](../../skills/video-review/), which carries the judgement — which document is being produced, what may be claimed. This tool carries the mechanics. The reasoning behind every default here, including two approaches that were tried and measured wrong, is in the skill's [DECISIONS.md](../../skills/video-review/DECISIONS.md).

## Known limits

- **Local files only.** No URL or hosted-video ingest. Deliberate, not an oversight.
- **Very small text edits are below the visual threshold** and the sweep will miss them. That is a trade for not drowning in near-identical frames. Cues cover it: if something mattered enough to say out loud, the visual pass does not need to notice it.
- **ffmpeg's scene filter is built for hard cuts** and fires barely at all on smooth or gradual change. On a lot of screen content the uniform top-up is doing the real work and deduplication is the control that matters.
- **Cue timing inherits whisper's timing**, which drifts by roughly half a second and has silent failure modes of its own (see [`tools/transcription/`](../transcription/README.md#known-limits)). Frames carry their real `ffprobe` timestamp in the manifest, so a mis-timed cue is visible on inspection rather than silent — but it is still a mis-timed cue.
- **`--effort large` and `average` behave the same** on a recording under about ten minutes with the default cap, because the budget tier table tops out below the ceiling either way. The dial has the most effect on long recordings.
- **The token estimate is an upper bound, not a prediction.** Actual spend comes in under it whenever the screen sits still, sometimes far under. Predicting the exact figure would mean deduplicating before extracting, which cannot be done without extracting.
- **JPEG output only**, quality fixed at `-q:v 2`. Fine for UI screenshots; not what you would choose for photographic detail.

## Setup

ffmpeg, ffprobe and Pillow. See [SETUP.md](SETUP.md) — two commands.

## Tests

```bash
python3 tools/video-frames/test_extract.py
```

33 tests, about ten seconds, standard library only. Fixtures are **generated** with ffmpeg at run time and thrown away, so there are no binaries in this repo and no assets to go stale. It runs on Linux and macOS in CI on every push.

Worth knowing what it is biased toward, because it explains the odd-looking assertions. Every data-integrity bug this tool has had was invisible to a happy-path test — the run exited zero, printed a success line, and produced correct-looking output while deleting a file it did not own, or filing a frame under the wrong recording. So a lot of these tests **assert what must not have happened**: that a planted file is byte-for-byte unchanged, that a refused command wrote nothing at all. Those are the ones worth keeping.

**Every documented guarantee here is also a test.** If a sentence in this README promises something — "never reduces cues", nothing unowned is deleted — it exists as an assertion, because a promise with nothing checking it is the thing that drifts.

The suite is mutation-checked: reintroducing each of the three bugs it was written for makes the corresponding tests fail, and reintroducing the original cue-sampling logic verbatim fails both cue tests. A suite that passes on broken code would be worse than none.

## Use

```bash
# What will this cost? Writes nothing. Shows all three effort tiers.
python3 tools/video-frames/extract.py probe walkthrough.mp4

# Frames + manifest, labelled with the transcript
python3 tools/video-frames/extract.py extract walkthrough.mp4 \
  --out walkthrough-frames --transcript walkthrough.srt

# Pin the moments that matter: explicit timestamps, or a word spoken out loud
  --cues 12.5,48.0 --marker screenshot

# How hard to sweep visually (default average)
  --effort small | average | large

# Zoom in on one stretch (denser frame budget)
  --start 45 --end 60

# One directory per recording, not one shared scratch path — see the gotchas.

# A frame turned out not to show what was discussed: fetch just that moment
  --append --cues 31.5

# The whole pass was too sparse: sample halfway between what you already have
  --refine

# Which frame supports which finding? Run this BEFORE reading any frames.
python3 tools/video-frames/extract.py map walkthrough-frames \
  --findings "D1=71.8,D2=95.6,V1=129.0"
```

`map` is the step that keeps a citing document affordable. Several findings routinely land on one image, so the distinct-image count runs far below the finding count — on a real 17-minute walkthrough, **28 images covered all 41 findings** out of 96 extracted. Read the mapped set rather than the folder and the same document costs **29%** of the ceiling. Full numbers: [DECISIONS.md](../../skills/video-review/DECISIONS.md#the-benchmark).

It also prints the thing a report otherwise gets wrong: **the filename is the capture time, not the finding time.** A shared image was taken at the earlier moment the screen last changed. Correct image, wrong second, and nobody assembling screenshots would guess that unaided.

Transcripts come from [`tools/transcription/transcribe.sh`](../transcription/). Both whisper `.json` and `.srt` are accepted.

## How frames get picked

Two signals, because in a screen recording **visual change and importance come apart**. Scrolling changes almost every pixel and means nothing; "and this bit is broken", said over a static screen, changes nothing and is the most important frame in the file.

- **Cues** are the moments that matter: timestamps passed in with `--cues`, or a keyword spoken aloud via `--marker`. They get reserved budget and survive deduplication.
- **Fill** is ffmpeg scene detection, topped up with uniform sampling, then deduplicated. It is the safety net for anything done silently, like clicking through screens without narrating.

**The frame budget is a ceiling, not a quota.** Coming in well under it is the good outcome: a 20-second static screen yields one frame, not twenty. Padding a budget with identical pictures is the exact waste this tool exists to prevent.

### Effort

`--effort small|average|large` scales the visual sweep. It **never scales cues down**: choosing `small` means leaning on the narration with a few visual references, not silently discarding a moment you flagged. If cues alone exceed the tier's budget, the ceiling rises to fit them.

Effort scales the **ceiling** as well as the budget beneath it. It has to: the tier table already reaches 100 frames on anything over ten minutes, so clamping an effort-scaled target to a fixed 100 made `large` silently identical to `average` on exactly the long recordings where more detail was being asked for. Unset, the ceiling is 35 / 100 / 200. Pass `--max-frames` and your number wins for every tier. Spend is gated by `probe` showing you the cost, not by this number.

### Going back for more

Both take a directory that already has a manifest and add to it, so you never re-send frames you have already looked at.

- `--append --cues 31.5` — one frame did not show what was being discussed. Fetch that moment, keep everything else.
- `--refine` — the whole pass was too sparse. Samples halfway between every pair of frames you already have, and runs no scene sweep.

A refine pass that finds nothing new **costs nothing**: the new samples collapse onto images already captured, so the distinct-image count and the token bill stay put.

### How "the same picture" is decided

By counting pixels that actually changed, at 64x64 in RGB, not by a perceptual hash.

This started as an 8x8 dHash, which is the standard tool for finding duplicate photos and is **wrong for screen recordings**. It reduces a frame to a coarse global signature, so a change confined to one region leaves the signature untouched. Measured on content that visibly changed, dHash returned a distance of **zero** and the frames were dropped as duplicates. A dropdown opening or an error banner appearing is exactly that shape of change. The full account is in [DECISIONS.md](../../skills/video-review/DECISIONS.md).

Calibrated by measurement rather than feel:

| | Measured |
|---|---|
| Noise floor, static screen frame to frame | **0.000%** |
| Small toast, 360x50 on a 1600x900 screen | 2.20% |
| Dialog, 600x300 | 14.5% |
| Full page navigation | 90.6% |
| **Default threshold** | **0.5%** |

Comparison is RGB rather than greyscale because colour carries meaning in a UI. In greyscale that page navigation measured 23% against ~90% of the screen actually changing, since the hue moved further than the brightness did. Red error states and green success states are the cases that matters for.

On real footage the noise floor is higher than the synthetic 0.000% — measured 0.024%–0.098%, as expected from anti-aliased text and a lossier encoder — and still 5–20x under the threshold. **Recalibrate against your own footage** if you are working with a very different source; a heavily compressed recording will raise the floor further.

## Gotchas

- **`--marker` cues are rewound by 1 second** (`--cue-offset`). Whatever you are describing is already on screen before you finish the sentence, so grabbing the frame where the words end catches the aftermath, not the subject. **`--cues` and `--refine` are absolute** and get no offset, because a targeted re-fetch or a midpoint means exactly the timestamp given. A caller deriving cues from a transcript should subtract the offset itself. This asymmetry is deliberate and was kept on purpose; the reasoning is in DECISIONS.md.
- **macOS screen recordings have a U+202F narrow no-break space** before the "pm" in their filename. It renders exactly like a normal space, so a hand-typed path silently fails with "video not found". Glob it (`ls ~/Desktop/*2.23.13*.mov`) rather than retyping it.
- **Pick a marker word you would not say by accident.** Whisper mishears, and a word that occurs naturally in your narration will fire cues you did not want.
- **Use one `--out` directory per recording, not a shared scratch path.** A fresh run clears the frames a previous pass recorded there, and `--append` refuses outright if the directory already holds a different recording. Both behaviours are deliberate, and both are much easier to live with when the directory belongs to one video. `walkthrough-frames` beside `walkthrough.mp4` is the whole convention. It also keeps a report's citations resolvable later, which `/tmp` does not.
- **The output directory is sensitive.** It holds stills of whatever was on screen. Delete it when you are done, or keep only the frames `map` says are cited and delete the rest.
- **Default long edge is 1568px, and that number is Claude's.** It is the standard-tier native maximum, so a 16:9 frame lands near 1,560 visual tokens with no downscaling penalty. Raise to 2000 to read small UI text; above 2000 the API applies a stricter per-image dimension cap once a request carries more than 20 images, and oversized frames get rejected. **On another provider, keep the frame selection and re-derive the resolution** — the arithmetic that produced 1568 is a Claude billing detail, but "pick a size where a frame is not silently downscaled, and stay under the many-image cap" is the transferable question. Frame counts, dimensions and the dedup threshold are provider-neutral; only the token conversion is not.
- **`--scene-threshold` defaults to 0.2** (the `average` tier), deliberately lower than a film default. A modal opening moves far fewer pixels than a hard cut.
- **The manifest is the contract.** Several entries can point at the same `file` when the screen did not change between them (`shares_image_with` says so). A consumer reading the manifest sends each distinct image once and attaches every timestamp and line to it; a consumer that just globs the folder gets the same set. Cost follows `distinct_images`, not entry count.

## Related

- [`tools/transcription/`](../transcription/) — produces the transcripts this consumes
- [`skills/video-review/`](../../skills/video-review/) — the skill that drives this
- [`skills/video-review/DECISIONS.md`](../../skills/video-review/DECISIONS.md) — why each default is the number it is, and what was measured wrong first
