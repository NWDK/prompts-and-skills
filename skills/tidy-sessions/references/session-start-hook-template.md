# Session-start hook template

Asks each new session to label and file itself. Fires on a fresh start only, so it stays quiet on resume and compaction. The hook cannot do the labelling. It plants one standing instruction in every session, whatever the task, and the session acts on it.

Needs `node` on your PATH. Only run on macOS. The title shape `<AREA>/<project> · <task>` is written into the instruction text below; change it there if yours differs. Fill in the mapping before installing: the placeholder entry would otherwise be printed into every session as written.

## 1. The handler

Save as `~/.claude/hooks/session-start-label.js` (user level, so it applies in every folder). Create the folder first with `mkdir -p ~/.claude/hooks`. Replace the one placeholder entry in `MAPPING` with one JSON object per group, taken from the live group list and confirmed with the user: `{ "area": "<AREA>", "group": "<Group name>" },`. Use double quotes, which handle apostrophes in a group name; write a double quote inside a name as `\"`.

```js
#!/usr/bin/env node
// SessionStart hook: asks a new session to title itself and file itself in a sidebar group.
let raw = '';
process.stdin.on('data', (d) => (raw += d));
process.stdin.on('end', () => {
  let input = {};
  try { input = JSON.parse(raw); } catch (e) {}
  if (input.source !== 'startup') return;

  const MAPPING = [
    { "area": "<AREA>", "group": "<Group name>" },
  ];

  const context = [
    'SESSION LABEL - do this once, as soon as you know what the task is, before substantive work.',
    'Skip all of it if this is a scheduled-task run (mcp__ccd_session_mgmt__get_session with session_id "self" shows scheduledTaskId).',
    'Also skip if you are in a terminal session (the session tools below do not exist there).',
    '',
    '0. If the tools below are deferred (listed by name only), load them first, in your FIRST batch of tool calls:',
    '   ToolSearch select:mcp__ccd_session_mgmt__get_session,mcp__ccd_session_mgmt__set_session_title,mcp__ccd_sidebar__list_groups,mcp__ccd_sidebar__move_sessions',
    '',
    '1. Title: mcp__ccd_session_mgmt__set_session_title({ session_id: "self", title: "<AREA>/<project> · <what you are doing>" }).',
    '   Skip if the title already has this shape.',
    '2. Group: call mcp__ccd_sidebar__list_groups for the LIVE list, pick the group, then',
    '   mcp__ccd_sidebar__move_sessions({ session_ids: ["self"], group_id: "<id>" }).',
    '   Pick the group by AREA:',
    ...MAPPING.map((m) => '     ' + m.area + ' -> ' + JSON.stringify(m.group)),
    '   Skip only if nothing genuinely fits.',
    '',
    'Why: other sessions identify you from the session list. An unlabelled session forces them to guess.',
  ].join('\n');

  process.stdout.write(JSON.stringify({
    hookSpecificOutput: { hookEventName: 'SessionStart', additionalContext: context },
  }));
});
```

## 2. The settings entry

Back up `~/.claude/settings.json` first. Then add this inside the top-level `"hooks"` object, creating that object if it isn't there:

```json
"SessionStart": [
  { "hooks": [ { "type": "command", "command": "node \"$HOME/.claude/hooks/session-start-label.js\"" } ] }
]
```

If a `SessionStart` array already exists, add the object to it. Do not replace what is there.

## 3. Check it

Start a new session. Within the first reply it should title itself and move into a group. Then run [`tidy-sessions`](../SKILL.md): the miss rate it reports is how often the hook was ignored. When a session skips it, type `/sort` in that session (the [`sort`](../../sort/SKILL.md) skill): it files that session at once and carries on.

Editing hooks and settings is refused in auto mode. Switch the mode picker to Manual before installing.

## 4. Remove it

Delete the `SessionStart` entry from `~/.claude/settings.json` and delete `~/.claude/hooks/session-start-label.js`.
