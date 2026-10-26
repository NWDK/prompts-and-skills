#!/bin/bash
# Builds into a scratch folder and checks the cleanup rule against planted files: which it would
# move, and that it leaves everything else alone. Leaves the installed copy and real shots alone.
#   bash test.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(cd "$(mktemp -d)" && pwd -P)"   # the real path: /var is a link to /private/var, and the app prints real paths
trap 'rm -rf "$T"' EXIT

APP_DIR="$T/apps" bash "$HERE/build.sh" >/dev/null
BIN="$T/apps/Screenshot Feedback.app/Contents/MacOS/ScreenshotFeedback"

F="$T/shots"
mkdir -p "$F/Keep" "$F/my-app"
plant() { touch "$F/$2"; touch -t "$(date -v-"$1"d +%Y%m%d%H%M)" "$F/$2"; }   # age in days, path
plant 20  2026-01-01_120000_App.png          # moved: inbox, over 14 days
plant 20  2026-01-01_120000_App.md           # moved: its note
plant 10  2026-01-02_120000_App.png          # kept: inbox, under 14 days
plant 20  notes.png                          # kept: not the app's own name
plant 20  2026-01-03_120000_App.txt          # kept: not a png or md
plant 100 Keep/2026-01-04_120000_App.png     # kept: keep/ is never swept, in any case
plant 20  my-app/2026-01-05_120000_App.png   # kept: project folder, under 30 days
plant 40  my-app/2026-01-06_120000_App.png   # moved: project folder, over 30 days
planted=$(cd "$F" && find . -type f | sort)

got=$(SCREENSHOT_FEEDBACK_FOLDER="$F" "$BIN" --clean-up-dry-run | sed "s|^$F/||" | sort)
want=$(printf '%s\n' 2026-01-01_120000_App.md 2026-01-01_120000_App.png my-app/2026-01-06_120000_App.png)
fail=0
[ "$got" = "$want" ] || { echo "FAIL cleanup picked:"; echo "$got"; echo "expected:"; echo "$want"; fail=1; }
[ "$(cd "$F" && find . -type f | sort)" = "$planted" ] || { echo "FAIL the dry run changed the folder"; fail=1; }
[ $fail = 0 ] && echo "ok: cleanup picks exactly the 3 expired shots and moves nothing on a dry run"
exit $fail
