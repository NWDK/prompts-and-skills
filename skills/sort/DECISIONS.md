# Decisions: sort

**It acts at once.** `tidy-sessions` waits for a go because it changes many sessions. This changes one, with one rename and one move, and you have just typed the command. The app may still ask you to approve a rename over a title you set.

**It carries on afterwards.** It is meant to be typed mid-task, so it reports one line and resumes.

**It never invents a title convention.** With no shared shape there is nothing right to impose. It says so and points at `tidy-sessions`, which proposes one for you to change.
