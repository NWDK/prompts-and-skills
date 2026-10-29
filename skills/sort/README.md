# sort

Type `/sort` in a Claude desktop app Code-tab session that has no clear title or sidebar group. It titles and files that one session, then carries on with the work it was doing.

It is the one-session fallback for the hook in [`tidy-sessions`](../tidy-sessions/README.md#the-set), which asks new sessions to file themselves and is sometimes skipped.

## Known limits

- Tried once by its author on a real session; it worked.
- Needs the Code tab's session and sidebar tools. Not checked in the terminal CLI.
- Learns your title shape and groups from your 40 most recent sessions. With no shared shape it won't invent one: run `tidy-sessions` first.

## What it reads and writes

Reads this session's details and the titles and groups of your 40 most recent sessions, plus your hook file's group mapping if you installed one. That content reaches the model like anything else you do in Claude.

Writes only this session's title and group, with no confirmation step of its own: the app asks you to approve a rename only if you set the current title yourself. It never touches another session or any group, never archives anything, and skips scheduled runs. To undo it, rename the session or move it back.

## Using it

Copy `sort/` and `tidy-sessions/` into `~/.claude/skills/` (or a project's `.claude/skills/`), then type `/sort` in the session that needs it. See [`DECISIONS.md`](DECISIONS.md) for the reasoning.
