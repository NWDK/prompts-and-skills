# Compatibility

Every provider-specific number this skill depends on, in one place, with the
date it was checked. Frame counts, frame dimensions and the deduplication
threshold are provider-neutral. Only the token conversion is not.

**Checked 2026-08-25** against
[platform.claude.com/docs/en/build-with-claude/vision](https://platform.claude.com/docs/en/build-with-claude/vision).

## Visual token cost

Claude bills images in 28x28 pixel patches. One image costs:

```
ceil(width / 28) * ceil(height / 28)
```

`extract.py` implements exactly this in `_image_tokens()`. On another
provider, the frame selection still holds and only this conversion changes.

## Resolution tiers

Two tiers, and which one you're on changes both the cost and the useful
frame size:

| Tier | Models | Max long edge | Max visual tokens |
|---|---|---|---|
| High-resolution | Claude 4.7 and later | 2576 px | 4784 |
| Standard | Everything else | 1568 px | 1568 |

Images above a tier's limit are downscaled before processing, which caps
the cost but also caps the detail.

**The tool defaults to a 1568 px long edge.** That's the standard tier's
native maximum, where a 16:9 frame lands near 1,560 tokens with no
downscaling penalty. On a high-resolution model the same frame is well
under the limit, so if you're reading small UI text and you're on Claude
4.7 or later, raising `--long-edge` buys real detail. It also costs up to
about three times more per frame, which is why it isn't the default.

## Request limits

- 600 images per request; 100 for models with a 200k context window.
- 32 MB per request on standard endpoints. With many frames you'll hit
  this before the image count.
- 8000x8000 px and 10 MB per image on the Claude API.
- **Over 20 images in one request, a stricter per-image dimension limit
  applies to every image in it.** Keep each frame at or below 2000 px on
  the long edge, or keep the request to 20 images. This is the reason the
  skill maps findings to frames and reads the mapped set rather than the
  folder.

## When these change

The formula has been stable. The tiers and limits are the parts that move.
If a run gets rejected or the printed estimate stops matching your bill,
recheck the page linked above and update this file rather than the numbers
scattered through the docs. The measured figures elsewhere in this skill
are records of real runs, not predictions, so they don't need updating when
these change.
