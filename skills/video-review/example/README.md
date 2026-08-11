# Worked example

A complete run, end to end, so you can see what this skill produces before deciding whether to install anything.

**Start with [report.md](report.md).** That is the deliverable. Everything else here exists to prove it was produced by the real pipeline rather than written to look good.

| File | What it is |
|---|---|
| [`report.md`](report.md) | The output — a defect log with every claim cited, and four declared gaps |
| [`make-example.sh`](make-example.sh) | Regenerates everything below. Real `extract.py`, shipped defaults, no mocks |
| [`checkout-walkthrough.transcript.srt`](checkout-walkthrough.transcript.srt) | The narration |
| `checkout-walkthrough.mp4` | Generated, not committed |
| `checkout-walkthrough-frames/` | Generated, not committed — frames plus `manifest.json` |

```bash
./make-example.sh        # needs ffmpeg + Pillow; ~5 seconds
```

## Two things it is honest about

**The recording is synthetic** — coloured rectangles standing in for a checkout page, built by ffmpeg. Nothing real was recorded, and the frames carry no readable text.

**That turns out to be the useful part.** Because the frames cannot show text, the report has to declare four gaps it would rather fill, including one where the narration describes a validation error and the frame can only confirm that *something red is in the wrong place*. A report that closed that gap by inference would read better and be partly invented. Watching it refuse is more informative than any polished sample would be.

**The writing step is not scripted.** The script builds the recording and runs extraction and mapping; `report.md` was then written by a model reading those frames and following `SKILL.md`. That division is the skill: the deterministic parts are a pipeline, the judgment is not, and generating the report from a template would misrepresent what this does.

## What to notice

- **24 seconds of video collapses to 3 distinct images**, and the report needed only 2 of them. ~5,376 visual tokens against a 43,008 ceiling. Most of a walkthrough is a screen that is not moving.
- **Two findings cite the same image, captured at neither of their timestamps.** The report says so. Nobody assembling screenshots by hand would think to.
- **A reaction stayed a reaction.** *"I don't love how much green there is"* is logged as an open question, not filed as a defect, because the speaker was expressing a preference and the two go to different people.
- **The one thing explicitly confirmed as correct is carried too**, so the devs know what not to touch.
