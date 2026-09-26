# Release checklist

The second pass: sanitising rewrites words; this checks the files that
ship, every time, against the staged diff, not the working tree.

## Before you look at content

- **Read `git status` two-letter codes, not the file list**: `MM` means
  staged and modified since.
- **Separate unpushed commits from staged changes**: they can be different
  intentions.
- **Check what is ignored, not just tracked**: `git status --porcelain
  --ignored`.

## Content, on the staged diff

- **Grep for your own markers**: employer, product, colleagues, hosts,
  your paths.
- **Scan for secrets mechanically**: entropy and credential patterns. A
  nameless credential passes sanitisation.
- **Check the history, not just the current tree**: a secret removed last
  commit is still in the one before.
- **Check author metadata**: commits carry the email configured at the
  time; use a noreply address.
- **Audit every claim for its real scope**, especially "local", "no
  network", "nothing is uploaded": a truth about one part, stated as a
  claim about the whole.
- **Re-derive any number from its source**, or delete it, rather than
  copy one doc-to-doc.
- **Check licences and adapted material**: anything adapted from someone
  else's work keeps their licence terms and credits them with a link.
- **Strip embedded file metadata**: images and documents carry authors,
  locations and edit history (EXIF, document properties).
- **Check what shipped code does on the network**: grep for URLs and
  network calls; each one should be documented.

## Things that resolve for you and not for anyone else

- **Follow every link. Not eyeball, follow.**
- **Check anchors after any heading change**: renaming breaks every link
  into it.
- **Check references to things you did not publish**: a workspace-only
  sibling sends a stranger nowhere.

## Does it still work

- **Run the tests, on the staged tree.**
- **Read every fenced code block that changed**: a prose sweep can
  reformat a command.
- **Follow your own README in a scratch directory, repo files only.**
  Anything you need from outside is a documentation bug.

## Then

Record in both copies that a public one exists, and which direction fixes
flow. Owner approves the final diff; push after.
