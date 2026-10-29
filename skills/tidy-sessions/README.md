# tidy-sessions

Gives your Claude desktop app Code-tab sessions a clear title and a sidebar group, working from the sessions and groups you already have. It proposes first and changes nothing until you say go. It can also install an optional hook that asks every new session to file itself.

Why: a session called "Fix it" in no group is hard to find, and hard for another session to message without guessing.

## The set

| Part | What it does |
|---|---|
| Hook (optional) | Asks each new session to title and file itself. Best-effort: an agent can skip it. [Template](references/session-start-hook-template.md) |
| [`/sort`](../sort/) | Type it in one session that missed. It files that session at once, then carries on with its work. |
| `tidy-sessions` (this skill) | Sorts many sessions at once. Proposes, waits for your go, and reports how often the hook was skipped. |

Install `tidy-sessions` and `sort` together.

## Known limits

- Built on one account that already had a title convention and groups. With none, the proposal states a convention at the top for you to change before anything is touched.
- Needs the Code tab's session and sidebar tools. Not checked in the terminal CLI. The hook template has only been run on macOS.
- The hook is best-effort: on the account it was built on, 22 of 102 non-scheduled sessions among the 250 most recent were unlabelled (some predate the hook). Each run reports its own count.

## What it reads and writes

Reads: session titles, folders and group names; scheduled-task names and run lists (to set scheduled runs aside); the last few messages of sessions whose title says nothing. All of it reaches the model like anything else you do in Claude.

Writes: titles, group membership and new groups, only after your go. It never archives or deletes a session, never renames or deletes a group, and never touches scheduled or archived sessions. The report lists each session's old title and group, so you can reverse any change by hand. The hook is a separate yes: it creates `~/.claude/hooks/session-start-label.js` and adds one `SessionStart` entry to your Claude settings.

## Using it

Copy `tidy-sessions/` and `sort/` into `~/.claude/skills/` (or a project's `.claude/skills/`), then say "tidy my sessions" or run `/tidy-sessions`. You get counts, a table of proposed titles and groups with a confidence on each, and questions for anything it couldn't place.

## The hook

Optional. It adds one instruction to every new session: load the session tools, title yourself, file yourself, and skip if you're a scheduled or terminal session. It reads nothing and calls no tools. It needs `node`. Install, check and removal steps are in [the template](references/session-start-hook-template.md); editing hooks and settings is refused in auto mode, so switch the mode picker to Manual first.

See [`DECISIONS.md`](DECISIONS.md) for the reasoning.
