# Worked example

A complete run, so you can see the output before installing anything. **Start with [report.md](report.md).**

| File | What it is |
|---|---|
| [`report.md`](report.md) | The output: a defect log where each item leads with what's wrong, where, what to do and whose it is |
| [`app/`](app/) | A stub of the checkout the recording shows. The resolve step reads it |
| [`make-example.sh`](make-example.sh) | Regenerates the recording and frames with the real `extract.py` and shipped defaults |
| [`checkout-walkthrough.transcript.srt`](checkout-walkthrough.transcript.srt) | The narration |
| `checkout-walkthrough.mp4`, `checkout-walkthrough-frames/` | Generated, not committed |

```bash
./make-example.sh                          # needs ffmpeg + Pillow; about 5 seconds
python3 -m http.server 8000 -d app         # optional: click through the stub at 1600x900
```

## What's synthetic

The recording is coloured rectangles drawn by ffmpeg, with no readable text. The app is a stub written for this example; the recording isn't a capture of it, but both are built to the same geometry. The red block in the frame is 360x50 at (1180, 150) on a 1600x900 screen, and so is the `.banner` rule in [`app/src/styles.css`](app/src/styles.css).

## What the resolve step does here

The frames alone show a red block in the wrong place and then a green page. On their own they leave four questions open: is the red block an error, is there a postcode field and was it empty, is the green page a confirmation, and is the review step missing or skipped. The code answers all four:

- The red block is the postcode error. `showBanner()` is the only code that shows it, and only when the postcode is empty. So the field exists and was empty.
- The fix is already half-built: an inline slot for the message sits under the field, unused.
- The green page is the confirmation page. Its background is the only full-page green in the app, and the card matches `.confirmation-card`.
- The review step exists. A staging flag switches it off, so it's a decision for the flag's owner, not a bug. Whether production has the same value isn't in the repository, so that's the one gap left, and the flags file names who holds it.

`report.md` was written by a model reading the frames and the stub, following `SKILL.md`. The script covers only the deterministic part.

## What to notice

- Each item leads with what to act on. The defect has error, location, fix and owner. The decision item puts the decision where the fix would go. The open question has no fix.
- Each item still names its screen and file when lifted out on its own.
- The review-step item is a decision, not a defect. The code showed the step works and a setting turns it off.
- 24 seconds of video collapses to 3 distinct images, and the report needed 2: about 3,584 visual tokens against a 43,008 ceiling.
- Two items cite one image, captured at neither of their timestamps, and the report says so.
- The one thing confirmed as correct is listed with its location, so nobody changes it.
