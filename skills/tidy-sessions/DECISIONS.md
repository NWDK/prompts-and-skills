# Decisions: tidy-sessions

Numbers are from one account, the 250 most recent sessions.

**Scheduled runs are found by `scheduledTaskId`, never by title.** A scheduled "Morning briefing" looks like a chat. `get_session` carries the field; `list_sessions` doesn't. 148 of the 250 were scheduled runs. They are set aside in bulk from `list_task_runs`, which returns the same session ids (checked against 7 of 7 control sessions), with `get_session` on the rest as a check.

**The hook only plants an instruction.** A hook can't call the app's tools or see whether it was obeyed, so the count of unlabelled non-scheduled sessions is its only reader: 22 of 102 here.
