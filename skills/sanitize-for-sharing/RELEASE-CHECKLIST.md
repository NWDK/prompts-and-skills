# Release checklist

The second pass. Sanitising rewrites words in a file; this checks the exact
set of files that will actually ship. Run it after, every time, and run it
against the staged diff rather than the working tree.

This is what I run. It has caught things in my own repo that I was certain
were clean.

## Before you look at content

**Read `git status` two-letter codes, not the file list.** `MM` means
staged and modified since. Something is still editing it, and you are about
to publish a mid-edit snapshot.

**Separate the change sets.** Unpushed commits and staged changes are
different things and can be different intentions. Review them apart. A
punctuation sweep and a factual correction bundled into one commit means
the log will say "punctuation" over a claim that changed.

**Check what is ignored, not just what is tracked.** `git status
--porcelain --ignored`. Confirm the ignored things are ignored on purpose,
and that nothing you need is among them.

## Content, on the staged set

**Grep for your own markers.** Employer, product, colleagues, internal
hosts, absolute paths with your username in them. Then grep the staged diff
specifically, because that is what ships.

**Scan for secrets mechanically.** Entropy and credential patterns, not
reading. Sanitisation misses any credential that carries no recognisable
name, which is most of them.

**Check the history, not just the current tree.** A secret removed in the
last commit is still in the one before it.

**Check author metadata.** Every commit carries the email you had
configured when you made it. On a public repo that address is harvestable.
GitHub's noreply address routes to you without publishing it.

## Things that resolve for you and not for anyone else

**Follow every link.** Not eyeball, follow. Placeholders and constructed
URLs are fine, but you should know which is which.

**Check anchors after any heading change.** Renaming a heading breaks every
link into it silently.

**Check references to things you did not publish.** A doc pointing at a
sibling piece that only exists in your workspace tells a stranger to go
looking for something that is not there.

## Does it still work

**Run the tests, on the staged tree.**

**Read every fenced code block that changed.** A sweep that reformats prose
will happily reformat a command.

**Follow your own README in a scratch directory, with the repo files only.**
Anything you have to know from outside the repo is a documentation bug.

## Then

Have the owner read the final diff and approve it. Push after that, not
before.
