# Decisions

Why this skill and its two tools are shaped the way they are, including the parts that were built wrong first.

This exists because a threshold with a measurement behind it is a decision, and the same number without one is a guess wearing a lab coat. Several numbers in this tool look arbitrary. None of them are, and the way to check that is to read what was measured.

Two things worth knowing before the detail:

- **Every measurement below came from running the thing**, on a synthetic test recording first and then on a real 17-minute product walkthrough (3836x2110, 75fps).
- **The two approaches that turned out to be wrong were both the standard, obvious choice.** That is the useful part. A perceptual hash for deduplication and greyscale for image comparison are what you would reach for, and measurement said no to both.

---

## 1. Four alternatives were vetted before any code was written

Claude has no native video input. The Messages API accepts `image`, `text` and `document` blocks only, and animated GIFs are flattened to their first frame. **That input contract is the whole constraint**, and it means any tool in this space is doing the same three things underneath: extract frames with ffmpeg, build a transcript, pass the frames in as images. Every candidate reviewed here did exactly that, and it is what this one does too.

Which reframes the question usefully. If the pipeline is fixed, then nobody's tool gives the model a new sense — the only things that differ are **which frames get chosen, and what a tool drags in with it.** That is a much smaller question than "which of these should we use", and it collapsed two of the four candidates immediately.

That makes "should we build this at all" a real question, and four existing projects were reviewed before answering it. Two are named below, because that is where the credit and the useful pointers are. Two were rejected, and rather than describe them, here are the criteria they failed — which is the part you can actually reuse.

### What disqualified a candidate

These are checks worth running against anything in this space, not verdicts on anyone in particular. Every one of them ruled something out during this survey.

- **Does it load when you did not ask it to?** A skill that registers an always-on session hook is in your context on every run, whether or not the task has anything to do with video.
- **Where does the audio go?** Several tools read as local and send audio to a hosted transcription API. For a screen recording that is the single most sensitive artefact in the pipeline, and "it's only a walkthrough" is exactly the assumption that gets something uploaded that should not have been.
- **What does it print to stdout?** An agent reads that stream as data. Anything written there — a banner, a promotion, an upsell — is being fed to a model as though it were part of the task.
- **What is committed?** A vendored virtualenv or bundled model weights in version control means every clone pays for them forever, and it quietly makes the author responsible for someone else's security updates.
- **How much of it would you actually use?** A platform with its own runtime, browser automation, OCR and a REST API is not a wrong project, but adopting it for one job means owning all of it.

Most of those are about what a tool does to *you* rather than how well it does its job, which is why reading the source matters more than reading the README.

### The two worth pointing at

| Verdict | Why |
|---|---|
| **Park** — [`oxbshw/watch-skill`](https://github.com/oxbshw/watch-skill) | Well engineered, and a whole platform: many model providers, a browser automation stack, its own runtime, OCR, a REST API. **If what you actually need is cross-video search or a persistent index, go there rather than here** — this tool deliberately does neither. |
| **Adapted a pattern from** — [`gallidigital-lang/claude-skill-video-to-spec`](https://github.com/gallidigital-lang/claude-skill-video-to-spec) | Little maintenance history and written in Portuguese, but carrying the single best idea found in the survey. Credited below. |

**What was taken, and it is the most useful finding here.** Two of the four independently converged on the same frame-selection design: a duration-scaled frame *budget* rather than a fixed capture rate, plus transcript-derived cue timestamps that are pinned and never dropped by deduplication. That was `watch-skill` and one of the skipped projects — two teams arriving at the same shape without coordinating, which is the strongest signal available that it is the right shape. It is the design this tool uses.

**From `video-to-spec` came the rule that governs this entire skill: a gap is declared, never filled.** Plus the discipline of deciding up front which document is being produced, because "write up this recording" is ambiguous enough that you can do excellent work and deliver the wrong artefact — its four archetypes are the direct ancestor of the three in `SKILL.md`.

No code was taken from any of them; these are ideas, independently implemented. But an idea that good deserves an address, and if you are reading this to decide what to trust, the same is true in reverse: you can go and check what it actually says.

**What was rejected and rebuilt instead** was the missing piece all four had in common: a deliberate, measured frame-*selection* step. That is the only thing this tool adds. Transcription, ffmpeg orchestration and the surrounding pipeline were all things that already existed.

### The one non-negotiable: local transcription only

There is no cloud path in either tool. Not a setting, not a fallback, not an environment variable. This is what disqualified the most popular candidate, and it is worth being explicit about the reasoning rather than treating it as ambient caution.

**The audio in a screen recording is more sensitive than it looks.** Someone narrating a walkthrough is talking over unreleased features, pre-launch pricing, landing pages that are not live, and customer data on screen. "It's only a marketing page" is exactly the assumption that gets something uploaded that should not have been, and the person recording is not going to stop mid-sentence to make that call.

An absent capability cannot be used by accident under time pressure. A configurable one will be.

---

## 2. Deduplication: the standard tool was measurably wrong here

**This is the single most important thing in this document**, because it is a case where the obvious choice fails silently, on the primary use case, while appearing to work.

Deduplication started as an **8x8 dHash** — a perceptual hash, the standard instrument for finding duplicate photos, and what almost anyone would reach for.

It is wrong for screen recordings, and not marginally. A perceptual hash reduces a whole frame to a coarse global signature. A change confined to one region of the picture leaves that signature untouched. Measured on real content, **frames with an obviously different panel on screen scored a dHash distance of exactly zero** and were dropped as duplicates.

Now look at what a screen recording is made of. A dropdown opening. An error banner appearing. A single field turning red. A toast sliding in. Every one of those is a localised change, and every one of them is precisely the frame most worth keeping. The tool would have discarded exactly the frames it exists to find, on its main use case, and reported a healthy-looking frame count while doing it.

**It passed the first test video only because those changes were full-frame colour swaps** — a synthetic case that a global signature handles fine and that told us nothing about real footage.

**Replaced with:** a per-pixel comparison at 64x64, counting the fraction of pixels that materially changed (more than 10 levels of difference on any channel). Localised change stays visible because localised change is exactly what a per-pixel count sees.

**What that trade costs:** blindness to very small text edits, which fall under the threshold. That is accepted deliberately and is documented as a known limit in three places. Cues cover it — if something mattered enough to say out loud, the visual sweep does not need to notice it independently.

---

## 3. The 0.5% threshold sits in a measured gap

Having chosen "fraction of pixels changed", the question becomes: what fraction counts as a different picture? Too low and every frame is kept along with the compression noise; too high and real UI changes are dropped.

The number was set by measuring both ends and putting the threshold in the space between them.

| What was measured | Result |
|---|---|
| Noise floor — two static frames, synthetic recording | **0.000%** |
| Noise floor — two static frames, real footage | 0.024% – 0.098% |
| Smallest change worth catching — a 360x50 toast on a 1600x900 screen | **2.20%** |
| A 600x300 dialog | 14.5% |
| A full page navigation | 90.6% |
| **Default threshold** | **0.5%** |

So 0.5% sits above the worst measured noise floor by 5–20x, and below the smallest real signal by about 4x. It is not a round number chosen because it sounds reasonable; it is the middle of an empty measured band.

The real-footage floor being higher than the synthetic 0.000% is expected and worth understanding: anti-aliased text and a lossier encoder both add per-pixel jitter to a screen that is not actually changing. That is also the reason to **recalibrate against your own footage** if your source is very different — a heavily compressed recording will push the floor up, and the headroom shrinks accordingly.

Confirmation on the real 17-minute run: the closest genuinely-different pair of kept frames measured 1.099%, so nothing that survived was anywhere near the line.

`--dedup-change` exposes the number, because the right value depends on your footage and pretending otherwise would be dishonest.

---

## 4. RGB, not greyscale, because hue carries meaning in a UI

Converting to greyscale before comparing images is a routine optimisation — three channels down to one, a third of the work, and for most computer vision tasks it costs nothing that matters.

It was tried, and measured wrong:

> **A full page navigation, visibly changing about 90% of the screen, measured 23% in greyscale.** The hue moved much further than the brightness did, and greyscale discards precisely the axis that moved.

That gap is not a rounding error, it is a four-fold underread on the largest possible change. And in a user interface the cases it hurts are the ones you care about most: **a red error state and a green success state can sit at nearly identical brightness.** In greyscale they are close to the same picture. A tool that cannot tell a failure state from a success state is not doing the job.

So comparison runs in RGB at 64x64. Three bytes per pixel instead of one, on a 64x64 thumbnail — the cost is irrelevant and the correctness is not.

---

## 5. The frame budget is a ceiling, not a quota

The budget caps frame *count* rather than setting a capture *rate*, because count is what costs money. Deriving the rate from the duration also means a long recording is automatically sampled more sparsely instead of blowing the budget, and nobody has to guess a sensible fps up front.

The first working version then made the natural mistake: it treated the budget as a target to fill, topping up with uniform samples **after** deduplication.

**Measured on a 30-second test video: 30 frames, of which 4 were distinct pictures.** Twenty-six byte-identical duplicates, roughly 43,000 tokens spent showing Claude the same screen over and over. That is the exact waste the tool exists to prevent, produced by the tool itself, while its console output looked like a full and healthy run.

**Two changes fixed it:**

1. The uniform top-up now happens **before** deduplication, so padding is removed rather than added last.
2. Coming in under budget is treated as a correct outcome, not a shortfall. Where entries survive over an unchanged screen — a cue raised while nothing moves, which is the common case, not the exception — they collapse onto a single shared image (`shares_image_with`) and keep their own timestamps and spoken lines without paying for the pixels twice.

| | Before | After |
|---|---|---|
| 30s test video | 30 frames / 4 distinct / 53,760 tokens | 6 entries / 4 distinct / **7,168 tokens** |
| Fully static 20s recording | 20 near-identical frames | **exactly 1 frame** |

This is why the tool prints how far *under* budget it came and how many tokens that saved. Without that line, an under-budget run reads as a failure and the next person "fixes" it by raising the budget.

The same reasoning is why the pre-flight estimate is an **upper bound and not a prediction**. An early acceptance check asked for the estimate to land within about 10% of actual — which quietly assumed the budget was a quota. Once under-budget became the correct outcome, a tight match would have meant the tool was padding. Predicting the exact figure would require deduplicating before extracting, which cannot be done without extracting.

**The cost is always shown before it is spent.** `probe` writes nothing and prints the frame budget and token ceiling for all three effort tiers. The estimate belongs at the point where the choice is still available, not in the summary afterwards.

---

## 6. Two bugs found by testing, one of them introduced by the fix for the other

Worth recording because of *how* they were caught, and because the second is the more instructive.

### The fix that broke something else

**`--effort large` was a no-op on any recording over about ten minutes.** The duration tier table already returned the default cap at that length, so the effort multiplier was applied and then immediately clamped away. `large` and `average` both produced 100 frames — the dial silently stopped working at exactly the long recordings where someone asking for more detail most needs it.

The fix was to make effort scale the ceiling as well as the budget beneath it.

**That fix contained its own bug.** The tier table was reading `max_frames` as its own base, so once the cap was effort-scaled the multiplier got applied twice. `--effort small` fell from 35 frames to 12 — a 3x under-sample, arriving as a side effect of fixing an unrelated dial, and nothing about it would look wrong from the outside. The tier table is now independent of the cap.

The general shape is worth keeping: a fix that changes a value another calculation reads as its input can multiply through twice. Neither the original bug nor the bug in its fix produced an error, a warning, or anything visibly different in the output. Both produced a plausible number.

### The check that caught the other two

Two separate multi-pass bugs, both found by **asserting the manifest against the disk** at the end of every run:

1. When one frame collapsed onto another, its file was unlinked — but any *later* entry already sharing that file was left pointing at a deleted path. Fixed by deciding collapses per file and then remapping every entry, rather than deciding per entry.
2. Frame names derive from their timestamp, so an `--append` pass regenerated identical names, overwrote the first pass's frames, and then dropped them as already-covered. Fixed with collision-free naming.

**Neither was visible from the console output.** Both runs looked successful. They were caught only because the tool ends by checking that every file on disk appears in the manifest *and* every manifest entry has a file on disk, and dies loudly if not.

That check cost about ten lines and found two real bugs on the day it was added. It stays.

---

## 7. Deliberately not changed: the `--cues` / `--marker` asymmetry

`--marker` cues are rewound by one second (`--cue-offset`), because whatever you are describing is already on screen before you finish the sentence — grabbing the frame where the words end catches the aftermath, not the subject.

`--cues` and `--refine` are **absolute** and get no offset.

This inconsistency was reviewed and kept. Which behaviour a caller wants is genuinely ambiguous: a targeted re-fetch of a specific second means *that second*, and `--refine`'s midpoints are meaningless if shifted. Making them uniform would trade a documented quirk for a silent surprise, and it is documented in three places including the `--help` text.

Callers deriving cues from a transcript subtract the offset themselves. The skill's cue-pass brief says so explicitly.

---

## 8. Model tiering: most of this pipeline uses no model at all

Worth stating because the intuition usually runs the other way.

| Step | Runs on |
|---|---|
| Transcribe, extract frames, deduplicate | **No model.** Local binaries — whisper.cpp and ffmpeg. |
| Pick which moments deserve a frame | **A text-only pass**, on the cheapest model that follows instructions. No image exists yet. A sub-agent if your host has them; same-thread if not. |
| Read the frames, write the document | **The vision-capable model.** The only step that needs the pictures, and the only one that cannot be downgraded. |

The transcript-first ordering is what makes this cheap. Cue selection happens *before* any frame exists, so it is a text-only call, and images enter context exactly once instead of being paid for by a sub-agent and then again in its report.

The expensive-*looking* parts of this pipeline — watching video, transcribing audio — are the free ones.

---

## 9. What the first real run proved, including one thing it caught

Run end to end on a 17-minute product walkthrough. Output: 18 defects, 9 variances, 9 open questions, 2 naming inconsistencies, and **5 claims explicitly marked not confirmed**.

### The benchmark

One table, rebuilt from the run's own `manifest.json` and the final report, because the first write-up of this mixed four different counts together and published the wrong two. Cues proposed, findings retained, manifest entries and distinct images are **four different numbers** and only the last one costs anything.

| | Count | Notes |
|---|---:|---|
| Cue moments proposed by the cue pass | 43 | from the transcript alone, before any frame existed |
| Findings retained in the final report | 41 | two proposed moments did not survive into findings |
| Manifest entries | 169 | across the initial sweep and later append passes |
| **Distinct images extracted** | **96** | entries collapse onto these; 52 entries shared an image |
| **Distinct images actually read** | **28** | the mapped set that covers all 41 findings |
| Visual tokens per frame | 1,736 | 1568px long edge on a 3836x2110 source |

**Ceiling** (all 96 distinct) = **166,656 tokens**. **Actual** (the 28 read) = **48,608**. So mapping first cost **29%** of reading the folder.

Two things that table is deliberately careful about. The 96 is *distinct images*, not the 169 manifest entries — cost follows pictures, not annotations. And the 28 is what the *report* cited, verified against the report itself rather than inferred from the manifest, because the two are separate records and the whole skill rests on not letting one impersonate the other.

**The declare-gaps rule earned its place immediately.** One narrated claim — that a set of paid add-ons were missing from an order summary — is **contradicted by its own frame**, which shows them present. Under a fill-in-the-gap approach, that would have gone to the developers as a bug that did not exist. Two further claims were only partially supported, and one was flatly unverifiable because the element had expired between samples.

The frames also surfaced two findings the narration never mentioned at all: a duplicated line of copy in a drawer, and a naming split between a tile and the drawer it opens. That is the case for the visual sweep existing alongside the cues.

---

## 10. Not built, on purpose

Both of these are parked with a stated trigger rather than sitting quietly on a roadmap.

**URL and hosted-video ingest.** Local files only. The download itself is easy; the anti-bot fallback ladder is what makes it expensive, and it was the bulk of the code volume in every candidate surveyed. *Trigger to build it: needing to review a video you cannot obtain as a file, such as a hosted interview or a competitor demo. Add it as a front-end acquire step, not a rewrite.*

**A manual marking harness** — scrub a video, tap to mark moments. Spoken markers and the semantic cue pass cover the self-recorded case, which is what this is for. *Trigger: reviewing someone else's footage with no narration to key off, such as silent B-roll. Even then, mark it in a real timeline editor and export, rather than building a bespoke player.*

Also deliberately absent: any cloud transcription path (section 1), video generation or editing, cross-video search or a persistent index, and real-time capture. Finished local files, reviewed once.

---

## API facts this relies on

Verified live against the vision documentation on 2026-08-11. Re-check before assuming they still hold.

- Image cost is `ceil(width / 28) x ceil(height / 28)` tokens. It follows output pixels, not file size.
- 1568px on the long edge is the standard-resolution tier's native maximum. A 16:9 frame lands near 1,560 tokens with no downscaling penalty — which is why it is the default rather than the 2000px ceiling.
- Above 20 images in a single request, a stricter per-image dimension cap applies and oversized images are rejected outright. This tool routinely exceeds 20 images, so the resolution ceiling is a default rather than an option.
- Limits at the time of checking: 600 images per request on 1M-context models, a 32 MB request ceiling (usually hit before the image count is), and 8000x8000px / 10 MB per image.
