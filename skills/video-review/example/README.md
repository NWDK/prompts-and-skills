# Worked example

A complete run, end to end, so you can see what this skill produces before deciding whether to install anything.

**Start with [report.md](report.md).** That is the deliverable. Everything else here exists to show it was produced by the real pipeline and checked against real code, rather than written to look good.

| File | What it is |
|---|---|
| [`report.md`](report.md) | The output: a defect log where every item opens with what is wrong, where, what to do and whose it is, cites a frame, and stands alone. One gap survived |
| [`app/`](app/) | A stub of the checkout the recording shows. The resolve step reads it |
| [`make-example.sh`](make-example.sh) | Regenerates the recording and frames. Real `extract.py`, shipped defaults, no mocks |
| [`checkout-walkthrough.transcript.srt`](checkout-walkthrough.transcript.srt) | The narration |
| `checkout-walkthrough.mp4` | Generated, not committed |
| `checkout-walkthrough-frames/` | Generated, not committed; frames plus `manifest.json` |

```bash
./make-example.sh        # needs ffmpeg + Pillow; ~5 seconds
```

The stub needs nothing to read. To click through it, serve it with any static file server and open it at 1600x900:

```bash
python3 -m http.server 8000 -d app      # then open http://localhost:8000
```

## What is synthetic, and why it still teaches the right thing

**The recording is synthetic**: coloured rectangles built by ffmpeg, carrying no readable text. **The app is a stub** written for this example, and the recording is not a capture of it. Both are built to the same geometry, so the frames and the code describe the same screen, the way a real recording and a real codebase do. The red block in the frame is 360x50 at (1180, 150) on a 1600x900 screen, and so is the `.banner` rule in [`app/src/styles.css`](app/src/styles.css).

**Frames alone give you symptoms.** Read without the app, this recording yields a red block in the wrong place, a green page, and four open questions: whether the red block is an error at all, whether a postcode field exists and was left empty, whether the green page is a confirmation, and whether the review step is missing or skipped. A report written from the frames alone would stop there and could pass off its refusal to guess as care. That is the failure, politely done: nothing invented, and nothing a developer could act on.

**The resolve step answers all four from the code**, and turns the last one into the only question worth asking:

- The red block is the postcode error. `showBanner()` is the only code that shows it, and it runs only when the postcode is empty.
- So the field exists and was empty. The same branch also shows the fix: an inline slot for the message already exists under the field, and nothing uses it.
- The green page is the confirmation page. Its background rule is the only full-page green in the app, and the card matches `.confirmation-card`.
- The review step is not missing. It exists, and a staging flag switches it off, which makes it a decision for whoever owns that flag rather than a bug. What the code cannot say is whether production has the same value, because production flags are not in the repository. That is the one gap in the report, and it names who can close it: the flags file says who holds production's values.

**The writing step is not scripted.** The script builds the recording and runs extraction and mapping. `report.md` was then written by a model reading those frames and the stub, following `SKILL.md`. That division is the skill: the deterministic parts are a pipeline, the judgment is not, and generating the report from a template would misrepresent what this does.

## What to notice

- **Every item leads with what to act on, before any evidence.** The defect: error, location, fix, owner. The decision item puts the decision where the fix would go. The open question has no fix at all. Stop reading there and you can still start work.
- **Lift any item out on its own** and it still names its screen and its file.
- **The review-step item is marked as a decision, not a defect, and says whose.** The code showed the step works and a setting turns it off. Calling that a bug would have been an invented consequence of a correct observation.
- **The one surviving gap is about production.** The recording never showed it, and the only file that sets flag values is the staging one.
- **24 seconds of video collapses to 3 distinct images**, and the report needed 2 of them: ~3,584 visual tokens against a 43,008 ceiling. Most of a walkthrough is a screen that is not moving.
- **Two items cite the same image, captured at neither of their timestamps.** The report says so. Nobody assembling screenshots by hand would think to.
- **A reaction stayed a reaction.** *"I don't love how much green there is"* is an open question for design, with a location, not a defect.
- **The one thing explicitly confirmed as correct is carried too**, with its location, so the devs know what not to touch.
