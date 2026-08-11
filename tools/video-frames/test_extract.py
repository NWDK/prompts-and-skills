#!/usr/bin/env python3
"""Regression tests for extract.py.

  python3 tools/video-frames/test_extract.py          # run everything
  python3 -m unittest discover tools/video-frames     # same, via unittest

Standard library only. Fixtures are GENERATED with ffmpeg at run time and thrown
away, so nothing binary is committed and the suite has no assets to go stale.
Skips cleanly with a clear message if ffmpeg is not installed.

WHAT THIS SUITE IS FOR, because it decides what belongs in it.

Every data-integrity bug this tool has had was invisible to a happy-path test. The
run exited zero, printed a success line, and produced correct-looking output -- while
deleting a file it did not own, or filing a frame under the wrong recording, or
dropping cues the caller had explicitly asked for. A suite that only asks "did it
produce the right frames?" answers yes to all three.

So the bias here is: assert what must NOT have happened. Several tests below check
that a file is byte-for-byte unchanged, or that nothing was written at all. Those
are the ones worth keeping when this file gets tedious to maintain.

Every documented guarantee is also a test. If a README sentence promises something
("never reduces cues", "nothing unowned is deleted"), it appears here as an
assertion, because a promise with nothing checking it is the thing that drifts.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACT = os.path.join(HERE, "extract.py")
TOOLS = os.path.dirname(HERE)


def have(binary):
    return shutil.which(binary) is not None


def run(*args, **kw):
    """Invoke extract.py as a subprocess and hand back the completed process.

    Deliberately not an in-process call: exit codes and the refusal-to-write
    behaviour are part of the contract being tested, and importing would let a
    test pass while the CLI was broken.
    """
    return subprocess.run([sys.executable, EXTRACT, *args],
                          capture_output=True, text=True, **kw)


def mkvideo(path, colour="red", seconds=4, size="320x180", rate=10, extra=None):
    """A solid-colour clip. Cheap, deterministic, and enough for frame selection."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "lavfi", "-i", f"color=c={colour}:s={size}:d={seconds}:r={rate}"]
    if extra:
        cmd += extra
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", str(seconds), path]
    subprocess.run(cmd, check=True, capture_output=True)
    return path


def mkvideo_with_change(path, seconds=6, size="1600x900"):
    """A static screen with one small region changing partway through.

    This is the shape the deduplication threshold was calibrated against: a
    360x50 element on a 1600x900 screen, i.e. a change confined to one region.
    A global perceptual hash scores this at zero, which is why the tool counts
    pixels instead.
    """
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", f"color=c=0x1a2340:s={size}:d={seconds}:r=10",
         "-f", "lavfi", "-i", f"color=c=0xcc2222:s=360x50:d={seconds}:r=10",
         "-filter_complex",
         f"[0:v][1:v]overlay=x=1180:y=40:enable='gte(t,{seconds/2})'[v]",
         "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-t", str(seconds), path],
        check=True, capture_output=True)
    return path


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def manifest(d):
    with open(os.path.join(d, "manifest.json")) as f:
        return json.load(f)


def jpgs(d):
    return sorted(f for f in os.listdir(d) if f.endswith(".jpg"))


@unittest.skipUnless(have("ffmpeg") and have("ffprobe"),
                     "ffmpeg/ffprobe not installed — see SETUP.md")
class Base(unittest.TestCase):
    """Fixtures are built once for the whole suite; ffmpeg is the slow part."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="video-frames-tests-")
        cls.red = mkvideo(os.path.join(cls.tmp, "red.mp4"), "red")
        cls.blue = mkvideo(os.path.join(cls.tmp, "blue.mp4"), "blue")
        cls.changing = mkvideo_with_change(os.path.join(cls.tmp, "changing.mp4"))
        cls.srt = os.path.join(cls.tmp, "t.srt")
        with open(cls.srt, "w") as f:
            f.write("1\n00:00:00,000 --> 00:00:02,000\nfirst line\n\n"
                    "2\n00:00:02,000 --> 00:00:04,000\nsecond line\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def out(self):
        return tempfile.mkdtemp(dir=self.tmp)

    def plant(self, d, name="unrelated-family-photo.jpg"):
        """Put a file in the output directory that this tool did not create."""
        p = os.path.join(d, name)
        with open(p, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0not-really-a-jpeg-but-named-like-one")
        return p, read_bytes(p)


# --- destructive safety -------------------------------------------------------
# The tool takes a user-supplied --out. Everything here asserts absence of harm.

class UnownedFiles(Base):

    def test_unowned_file_survives_a_normal_run(self):
        d = self.out()
        p, before = self.plant(d)
        r = run("extract", self.red, "--out", d, "--effort", "small")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(p), "an unowned file was DELETED")
        self.assertEqual(read_bytes(p), before, "an unowned file was MODIFIED")

    def test_unowned_file_is_reported_not_silently_left(self):
        # Leaving it alone is necessary but not sufficient: anything that globs
        # the folder will still pick it up, so the run has to say so.
        d = self.out()
        self.plant(d)
        r = run("extract", self.red, "--out", d, "--effort", "small")
        self.assertIn("not written by this tool", r.stderr)

    def test_fresh_rerun_replaces_only_its_own_frames(self):
        d = self.out()
        p, before = self.plant(d)
        run("extract", self.red, "--out", d, "--effort", "small")
        first = jpgs(d)
        run("extract", self.red, "--out", d, "--effort", "small")
        self.assertTrue(os.path.exists(p))
        self.assertEqual(read_bytes(p), before)
        self.assertEqual(len(jpgs(d)), len(first), "frame count drifted across reruns")

    def test_unowned_file_named_like_ours_still_survives(self):
        # Ownership is tracked, not inferred. A file that merely LOOKS like our
        # output is still not ours -- this is the case a filename-pattern check
        # got wrong, and it is why the pattern check was replaced.
        d = self.out()
        p, before = self.plant(d, "cue_t00001.00.jpg")
        r = run("extract", self.red, "--out", d, "--effort", "small")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(p), "a lookalike unowned file was deleted")
        self.assertEqual(read_bytes(p), before)


class ManifestConsistency(Base):

    def test_every_manifest_entry_has_a_file_and_vice_versa(self):
        d = self.out()
        run("extract", self.changing, "--out", d, "--effort", "average")
        listed = {f["file"] for f in manifest(d)["frames"]}
        on_disk = set(jpgs(d))
        self.assertEqual(listed - on_disk, set(), "manifest points at missing files")
        self.assertEqual(on_disk - listed, set(), "stray frames not in the manifest")

    def test_distinct_image_count_matches_disk(self):
        d = self.out()
        run("extract", self.changing, "--out", d, "--effort", "average")
        m = manifest(d)
        self.assertEqual(m["distinct_images"], len(jpgs(d)))


# --- provenance ---------------------------------------------------------------

class SourceIdentity(Base):

    def test_append_from_a_different_video_is_refused(self):
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small")
        before = read_bytes(os.path.join(d, "manifest.json"))
        r = run("extract", self.blue, "--out", d, "--append", "--cues", "2.0")
        self.assertNotEqual(r.returncode, 0, "a cross-source append was accepted")
        self.assertIn("different recording", r.stderr + r.stdout)
        self.assertEqual(read_bytes(os.path.join(d, "manifest.json")), before,
                         "the manifest was modified by a refused append")

    def test_different_videos_of_identical_shape_are_still_distinguished(self):
        # The regression that matters: two solid-colour clips of the same
        # duration and dimensions encode to byte-identical SIZES, so a
        # metadata-only identity waves this through. Content is what decides.
        rmeta = json.loads(run("probe", self.red, "--json").stdout)["source"]
        bmeta = json.loads(run("probe", self.blue, "--json").stdout)["source"]
        self.assertEqual(rmeta["bytes"], bmeta["bytes"],
                         "fixture no longer exercises the identical-size case")
        self.assertEqual(rmeta["duration"], bmeta["duration"])
        self.assertNotEqual(rmeta["fingerprint"], bmeta["fingerprint"],
                            "different recordings share a fingerprint")

    def test_append_from_the_same_video_succeeds(self):
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small")
        n = len(manifest(d)["frames"])
        r = run("extract", self.red, "--out", d, "--append", "--cues", "2.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertGreater(len(manifest(d)["frames"]), n)

    def test_a_moved_but_unchanged_source_is_recognised(self):
        # Identity must not be the path, or renaming a recording silently
        # invalidates every manifest that cites it.
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small")
        moved = os.path.join(self.tmp, "red-renamed.mp4")
        shutil.copyfile(self.red, moved)
        r = run("extract", moved, "--out", d, "--append", "--cues", "3.0")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_append_without_transcript_keeps_prior_provenance(self):
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small",
            "--transcript", self.srt)
        run("extract", self.red, "--out", d, "--append", "--cues", "1.0")
        self.assertTrue(manifest(d)["transcript"],
                        "an append blanked the transcript provenance")

    def test_mixed_resolution_append_describes_each_frame_correctly(self):
        # The documented "go back at a higher resolution" workflow leaves a
        # collection holding more than one frame size. A single collection-level
        # figure then describes some of its own contents incorrectly while looking
        # authoritative -- the manifest lying about what it holds, which is the one
        # thing this tool must never do.
        from PIL import Image
        d = self.out()
        # Source must be LARGER than both resolutions or neither downscales and
        # the collection is not mixed at all -- the first version of this test used
        # a 320x180 source and passed while exercising nothing.
        run("extract", self.changing, "--out", d, "--effort", "small",
            "--resolution", "320")
        run("extract", self.changing, "--out", d, "--append", "--cues", "2.5",
            "--resolution", "640")
        m = manifest(d)
        self.assertGreater(len({(f.get("width"), f.get("height")) for f in m["frames"]}), 1,
                           "fixture no longer produces a mixed-resolution collection")
        seen, total = set(), 0
        for f in m["frames"]:
            if f["file"] in seen:
                continue
            seen.add(f["file"])
            with Image.open(os.path.join(d, f["file"])) as im:
                real = im.size
            self.assertEqual((f.get("width"), f.get("height")), real,
                             f"{f['file']}: manifest dimensions do not match the file")
            total += f["tokens"]
        self.assertEqual(m["estimated_visual_tokens"], total,
                         "cost was not summed from the actual frames")
        self.assertTrue(m["output"]["collection_is_mixed_resolution"],
                        "a mixed-resolution collection did not say so")

    def test_pass_history_survives_appends_with_different_settings(self):
        # Selection settings decide how hard the sweep looked. Keeping only the
        # latest set makes the manifest wrong about the coverage of every frame an
        # earlier pass contributed, which is the question a reader actually asks.
        d = self.out()
        run("extract", self.changing, "--out", d, "--effort", "small",
            "--dedup-change", "0.005")
        run("extract", self.changing, "--out", d, "--append", "--cues", "2.5",
            "--effort", "large", "--dedup-change", "0.03")
        p = manifest(d)["passes"]
        self.assertEqual(len(p), 2, "an append did not record its own pass")
        self.assertEqual([x["mode"] for x in p], ["fresh", "append"])
        self.assertEqual(p[0]["effort"], "small", "the first pass's settings were lost")
        self.assertEqual(p[0]["dedup_change"], 0.005)
        self.assertEqual(p[1]["effort"], "large")
        self.assertEqual(p[1]["dedup_change"], 0.03)

    def test_dedup_threshold_is_recorded_at_all(self):
        # It was absent entirely, so a single-pass manifest could not tell you
        # what threshold produced it.
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small",
            "--dedup-change", "0.02")
        self.assertEqual(manifest(d)["passes"][0]["dedup_change"], 0.02)
        self.assertEqual(manifest(d)["budget"]["dedup_change"], 0.02)

    def test_single_resolution_collection_is_not_flagged_as_mixed(self):
        d = self.out()
        run("extract", self.changing, "--out", d, "--effort", "average")
        self.assertFalse(manifest(d)["output"]["collection_is_mixed_resolution"])

    def test_prior_frames_are_not_overwritten_by_a_later_pass(self):
        # Frame names derive from the timestamp, so a second pass regenerates
        # identical names unless collisions are avoided.
        d = self.out()
        run("extract", self.changing, "--out", d, "--effort", "small")
        first = {f["file"]: os.path.getsize(os.path.join(d, f["file"]))
                 for f in manifest(d)["frames"]}
        run("extract", self.changing, "--out", d, "--append", "--cues", "0.5,1.5")
        for name, size in first.items():
            self.assertTrue(os.path.exists(os.path.join(d, name)),
                            f"{name} was removed by an append")
            self.assertEqual(os.path.getsize(os.path.join(d, name)), size,
                             f"{name} was overwritten by an append")


# --- the cue guarantee --------------------------------------------------------
# The docs promise effort "never reduces cues". That sentence is these tests.

class Cues(Base):

    MANY = ",".join(str(round(i * 0.09, 2)) for i in range(1, 41))

    def test_default_ceiling_grows_to_keep_every_cue(self):
        d = self.out()
        r = run("extract", self.red, "--out", d, "--effort", "small",
                "--cues", self.MANY, "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("sampling down", r.stdout)
        self.assertIn("cues   40", r.stdout.replace("  ", "  "))

    def test_explicit_cap_too_small_refuses_and_writes_nothing(self):
        d = self.out()
        r = run("extract", self.red, "--out", d, "--effort", "small",
                "--max-frames", "5", "--cues", self.MANY)
        self.assertNotEqual(r.returncode, 0, "an explicit cap silently dropped cues")
        self.assertIn("Refusing to choose", r.stderr)
        self.assertEqual(jpgs(d), [], "frames were written before the refusal")

    def test_cap_refusal_does_not_even_create_the_directory(self):
        # The first version of this test asserted "no .jpg files" and passed while
        # the run was creating the output directory anyway. "Writes nothing" means
        # nothing, and an assertion has to check the thing it claims to check.
        d = os.path.join(self.tmp, "never-created-by-refusal")
        r = run("extract", self.red, "--out", d, "--effort", "small",
                "--max-frames", "5", "--cues", self.MANY)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(d),
                         "a run that wrote nothing still created its output directory")

    def test_cues_survive_deduplication_on_a_static_screen(self):
        # The whole point of a cue: the screen has not changed, but the moment
        # matters. The entry must survive even though the picture is shared.
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small",
            "--cues", "1.0,2.0,3.0", "--transcript", self.srt)
        stamps = {f["timestamp"] for f in manifest(d)["frames"]}
        for t in (1.0, 2.0, 3.0):
            self.assertIn(t, stamps, f"cue at {t}s was dropped")


# --- selection behaviour ------------------------------------------------------

class Selection(Base):

    def test_static_video_collapses_to_one_distinct_image(self):
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "average")
        self.assertEqual(manifest(d)["distinct_images"], 1,
                         "a static recording produced more than one picture")

    def test_localised_change_survives_deduplication(self):
        # 360x50 on 1600x900. Small, and the reason a global hash was rejected.
        d = self.out()
        run("extract", self.changing, "--out", d, "--effort", "average")
        self.assertGreaterEqual(manifest(d)["distinct_images"], 2,
                                "a localised UI change was deduplicated away")

    def test_refine_on_a_static_video_adds_no_distinct_images(self):
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small")
        before = manifest(d)["distinct_images"]
        r = run("extract", self.red, "--out", d, "--refine")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(manifest(d)["distinct_images"], before,
                         "a refine pass that found nothing new still cost tokens")

    def test_dry_run_writes_nothing(self):
        d = self.out()
        r = run("extract", self.red, "--out", d, "--effort", "small", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(jpgs(d), [])
        self.assertFalse(os.path.exists(os.path.join(d, "manifest.json")))

    def test_dry_run_does_not_even_create_the_directory(self):
        d = os.path.join(self.tmp, "never-created-by-dry-run")
        r = run("extract", self.red, "--out", d, "--effort", "small", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(d),
                         "--dry-run created its output directory")

    def test_window_restricts_frames_to_the_range(self):
        d = self.out()
        run("extract", self.changing, "--out", d, "--start", "3", "--end", "5")
        for f in manifest(d)["frames"]:
            self.assertGreaterEqual(f["timestamp"], 2.9)
            self.assertLessEqual(f["timestamp"], 5.1)

    def test_probe_writes_nothing(self):
        d = self.out()
        r = run("probe", self.red)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(os.listdir(d), [])


# --- transcripts, mapping, and awkward paths ----------------------------------

class Transcripts(Base):

    def test_srt_is_parsed_and_labels_frames(self):
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small",
            "--transcript", self.srt, "--cues", "1.0")
        self.assertTrue(any(f.get("spoken") for f in manifest(d)["frames"]),
                        "no frame carried its spoken line")

    def test_whisper_json_is_parsed(self):
        j = os.path.join(self.tmp, "t.json")
        with open(j, "w") as f:
            json.dump({"transcription": [
                {"text": " hello", "offsets": {"from": 0, "to": 2000}},
                {"text": " there", "offsets": {"from": 2000, "to": 4000}}]}, f)
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small",
            "--transcript", j, "--cues", "1.0")
        self.assertTrue(any(f.get("spoken") for f in manifest(d)["frames"]))

    def test_unsupported_transcript_format_fails_clearly(self):
        bad = os.path.join(self.tmp, "t.vtt")
        with open(bad, "w") as f:
            f.write("WEBVTT\n")
        r = run("extract", self.red, "--out", self.out(), "--transcript", bad)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unsupported transcript format", r.stderr)


class AwkwardPaths(Base):

    def test_spaces_and_unicode_in_paths(self):
        # macOS screen recordings ship with spaces and a narrow no-break space
        # in their filenames, so this is the normal case, not an edge case.
        weird = os.path.join(self.tmp, "Screen Recording 2.23.13 pm — café.mp4")
        shutil.copyfile(self.red, weird)
        d = os.path.join(self.tmp, "out dir with spaces")
        os.makedirs(d, exist_ok=True)
        r = run("extract", weird, "--out", d, "--effort", "small")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(jpgs(d))

    def test_missing_video_fails_with_a_useful_message(self):
        r = run("probe", os.path.join(self.tmp, "nope.mp4"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("video not found", r.stderr)


class Mapping(Base):

    def test_map_reports_shared_images_and_capture_time(self):
        d = self.out()
        run("extract", self.red, "--out", d, "--effort", "small",
            "--cues", "1.0,2.0,3.0", "--transcript", self.srt)
        r = run("map", d, "--findings", "A=1.0,B=2.0,C=3.0", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["findings"], 3)
        self.assertLessEqual(out["distinct_images"], 3)
        shared = [row for row in out["rows"] if row["shared_with"]]
        self.assertTrue(shared, "identical screens did not share an image")

    def test_map_without_a_manifest_fails(self):
        r = run("map", self.out(), "--findings", "A=1.0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no manifest", r.stderr)


# --- the shell side -----------------------------------------------------------

class Shell(unittest.TestCase):
    """The install script and the transcription wrapper.

    Kept in this file so there is ONE command to run before shipping, rather
    than a python suite that passes while a shell script is broken.
    """

    def _syntax(self, rel):
        p = os.path.join(TOOLS, rel)
        if not os.path.exists(p):
            self.skipTest(f"{rel} not present")
        r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"{rel} has a syntax error:\n{r.stderr}")

    def test_transcribe_sh_syntax(self):
        self._syntax("transcription/transcribe.sh")

    def test_setup_sh_syntax(self):
        self._syntax("transcription/setup.sh")

    def test_setup_dry_run_installs_nothing(self):
        p = os.path.join(TOOLS, "transcription", "setup.sh")
        if not os.path.exists(p):
            self.skipTest("setup.sh not present")
        models = os.path.join(TOOLS, "whisper-models")
        before = sorted(os.listdir(models)) if os.path.isdir(models) else None
        r = subprocess.run(["bash", p, "--dry-run"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Nothing will be executed", r.stdout)
        after = sorted(os.listdir(models)) if os.path.isdir(models) else None
        self.assertEqual(before, after, "--dry-run touched the model directory")

    def test_setup_never_uses_elevated_privileges(self):
        # Rule 6 of the install-script contract in tools/README.md.
        p = os.path.join(TOOLS, "transcription", "setup.sh")
        if not os.path.exists(p):
            self.skipTest("setup.sh not present")
        with open(p, encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            code = line.split("#", 1)[0]
            self.assertNotIn("sudo ", code, f"setup.sh line {i} elevates privileges")

    def test_setup_never_pipes_the_internet_into_a_shell(self):
        # Rule 4. Downloads must land in a file you can inspect.
        p = os.path.join(TOOLS, "transcription", "setup.sh")
        if not os.path.exists(p):
            self.skipTest("setup.sh not present")
        with open(p, encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            code = line.split("#", 1)[0]
            if "curl" in code or "wget" in code:
                self.assertNotIn("|", code, f"setup.sh line {i} pipes a download")


if __name__ == "__main__":
    if not (have("ffmpeg") and have("ffprobe")):
        print("ffmpeg/ffprobe not installed — most tests will skip. See SETUP.md.",
              file=sys.stderr)
    unittest.main(verbosity=2)
