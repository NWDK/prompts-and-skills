# Decisions

Why this skill and its two tools are shaped the way they are. The measurements come from a synthetic test recording and from real product walkthroughs (the first 17 minutes long at 3836x2110 and 75fps; section 10 draws on a second, 27 minutes). The two approaches measured wrong (sections 2 and 4) were both the standard choice.

---

## 1. What already existed, and what was taken

Claude has no native video input: the Messages API accepts `image`, `text` and `document` blocks, and animated GIFs are flattened to their first frame. So every tool in this space does the same thing underneath: extract frames with ffmpeg, build a transcript, pass frames in as images. What differs is **which frames get chosen, and what the tool drags in with it.**

Four existing projects were reviewed before building. Two are named below; the other two are left unnamed, and the checks that ruled them out are the reusable part:

- **Does it load when you didn't ask?** An always-on session hook puts it in every context.
- **Where does the audio go?** Several tools that read as local send audio to a hosted transcription API.
- **What does it print to stdout?** An agent reads that as data, so a banner or upsell is fed to the model.
- **What is committed?** A vendored virtualenv or model weights make every clone pay forever.
- **How much would you use?** Adopting a platform for one job means owning all of it.

| Verdict | Project |
|---|---|
| **Park** | [`oxbshw/watch-skill`](https://github.com/oxbshw/watch-skill): well engineered, and a whole platform. Go there for cross-video search or a persistent index, which this deliberately doesn't do. |
| **Adapted a pattern from** | [`gallidigital-lang/claude-skill-video-to-spec`](https://github.com/gallidigital-lang/claude-skill-video-to-spec): the rule "a gap is declared, never filled", and deciding up front which document is being produced. Its four archetypes are the ancestor of the three here. |

Two projects independently converged on the frame-selection design used here: a frame **budget** scaled to duration, rather than a fixed rate, with transcript cues pinned so deduplication never drops them. No code was taken from any of them. What this adds is a measured frame-selection step.

**Transcription is local only, with no cloud path at all.** The audio of a narrated walkthrough is the most sensitive artefact in the pipeline, and a capability that doesn't exist can't be switched on by accident under time pressure.

## 2. Deduplication: a perceptual hash is wrong for screen recordings

It started as an 8x8 dHash, the standard tool for duplicate photos. A perceptual hash reduces a frame to a coarse global signature, so a change confined to one region leaves it untouched. On real footage, **frames with an obviously different panel scored a distance of zero** and were dropped. Screen recordings are made of exactly those local changes: a dropdown, an error banner, a toast. The first synthetic test passed only because its changes were full-frame colour swaps.

**Replaced with** a per-pixel comparison at 64x64: the fraction of pixels that changed by more than 10 levels on any channel. **The cost:** very small text edits fall under the threshold. Accepted, because cues catch anything said out loud.

## 3. The 0.5% threshold sits in a measured gap

| Measured | Result |
|---|---|
| Noise floor, static frames, synthetic | 0.000% |
| Noise floor, static frames, real footage | 0.024% – 0.098% |
| Smallest change worth catching: a 360x50 toast on 1600x900 | 2.20% |
| A 600x300 dialog | 14.5% |
| A full page navigation | 90.6% |
| **Default** | **0.5%** |

That is 5–20x above the worst noise floor and about 4x below the smallest real signal. On the 17-minute run, the closest pair of kept frames differed by 1.099%. Heavily compressed footage raises the floor, so recalibrate with `--dedup-change` if your source is very different.

## 4. RGB, not greyscale

Greyscale is the routine optimisation, and it measured wrong: **a page navigation that visibly changed about 90% of the screen measured 23% in greyscale**, because the hue moved much further than the brightness. In a UI, a red error state and a green success state can have nearly the same brightness. Comparing RGB at 64x64 costs nothing that matters.

## 5. The frame budget is a ceiling, not a quota

The budget caps frame count, because count is what costs money, and deriving the rate from duration means longer recordings are sampled more sparsely. The first version filled the budget, topping up with uniform samples after deduplication:

| | Before | After |
|---|---|---|
| 30s test video | 30 frames, 4 distinct, 53,760 tokens | 6 entries, 4 distinct, 7,168 tokens |
| Fully static 20s recording | 20 near-identical frames | 1 frame |

Two changes fixed it: the top-up happens **before** deduplication, and coming in under budget counts as correct. Entries over an unchanged screen share one image (`shares_image_with`) and keep their own timestamps. The tool prints how far under budget it came so nobody "fixes" an under-budget run by raising the budget. The pre-flight estimate is therefore an upper bound, not a prediction, and `probe` shows it before anything is spent.

## 6. Bugs found by testing

- **`--effort large` did nothing on recordings over about ten minutes**, because the tier table already returned the cap. The fix scaled the cap by effort, and in doing so applied the multiplier twice: `--effort small` fell from 35 frames to 12. Neither bug produced an error or a visibly wrong output. The tier table is now independent of the cap.
- **Two multi-pass bugs were caught by checking the manifest against the disk** at the end of every run: a collapsed frame's file was deleted while a later entry still pointed at it, and `--append` regenerated identical filenames and overwrote the first pass. Both runs looked successful. The check stays: every file on disk must be in the manifest and every entry must have a file, or the run fails loudly.

## 7. `--cues` and `--marker` differ on purpose

`--marker` cues are rewound by `--cue-offset` (one second), because what is being described is already on screen before the sentence ends. `--cues` and `--refine` are absolute: a targeted re-fetch means that second, and shifted midpoints would be meaningless. Callers deriving cues from a transcript subtract the offset themselves, as the cue-pass brief says.

## 8. Most of the pipeline uses no model

| Step | Runs on |
|---|---|
| Transcribe, extract, deduplicate | No model: whisper.cpp and ffmpeg |
| Pick the moments | A text-only pass on the cheapest model that follows instructions. No image exists yet |
| Resolve each item | The main model, reading the system under review alongside the mapped frames |
| Read the frames and write | The vision-capable model. The only step that can't be downgraded |

Picking cues before any frame exists means images enter context once, instead of being paid for by a sub-agent and again in its report.

## 9. The first real run

17-minute walkthrough. Output: 18 defects, 9 variances, 9 open questions, 2 naming inconsistencies, and 5 claims marked not confirmed.

| | Count |
|---|---:|
| Cue moments proposed by the cue pass | 43 |
| Findings retained in the report | 41 |
| Manifest entries, across the sweep and later append passes | 169 |
| **Distinct images extracted** | **96** |
| **Distinct images read** (the mapped set covering all 41 findings) | **28** |
| Visual tokens per frame (1568px long edge) | 1,736 |

Reading all 96 would cost 166,656 tokens; the 28 cost 48,608, so mapping first cost 29% of reading the folder. Cost follows distinct images, not manifest entries.

One narrated claim, that paid add-ons were missing from an order summary, was contradicted by its own frame, which showed them present. It went to the gap list instead of to the developers as a bug. The visual sweep also found two things nobody narrated: a duplicated line of copy, and a naming split between a tile and the drawer it opens.

## 10. The write-up stage needed its own steps

On the second real run the capture half held and the document didn't: four items reached a sent document and were withdrawn. In each, the observation was right and the consequence was invented, and each was answerable from code or a query already in reach.

The cause was structural. Seven of the loop's eight steps gathered evidence; writing was one step with four sentences of guidance. So:

- **"A gap is declared, not filled" was governing the output as well as the evidence**, which made handing back an unchecked item look like compliance. Step 6, Resolve, now sits between mapping and writing.
- **The defect-log spec described the recording** (timestamp, frame, what was said, what was visible) and nothing about the system. It's now error, location down to `file:line`, fix and owner, with a stand-alone test.
- **Smaller changes from the same run:** structure by product area, because ownership changes at area boundaries; the reviewer's priority order asked for at step 0; and narration outranks frames when they conflict. The run's worst error overrode someone's description of their own screen on one frame; re-extracting showed both things they'd described, twelve seconds apart. Together with section 9, that is the rule: never settle a conflict on one frame.

A separate write-up skill was considered and rejected: the write-up needs the frames, the transcript and the difference between them, which is what a handoff loses. The worked example was rebuilt at the same time around a stub app, so it shows items being resolved rather than gaps being declared. The rebuilt stage has since been used on two more real walkthroughs.

## 11. Not built, on purpose

- **URL and hosted-video ingest.** The download is easy; the anti-bot fallbacks are most of the code in every tool surveyed. *Build it when* you need to review a video you can't get as a file, as a front-end acquire step.
- **A manual marking harness.** Spoken markers and the cue pass cover self-recorded footage. *Build it when* reviewing silent footage with no narration, and even then mark it in a real editor and export.

Also absent on purpose: cloud transcription, video editing, cross-video search, real-time capture.

## API facts this relies on

The numbers live in [COMPATIBILITY.md](COMPATIBILITY.md), dated. What they decided:

- **The default long edge is the tier's native maximum.** Going higher buys detail you pay about three times over for.
- **The resolution cap is a default, not an option**, because this tool routinely sends more than 20 images, and above 20 the API applies a stricter per-image cap.
- **Cost follows output pixels, not file size**, so compression doesn't change the bill and resolution does.
