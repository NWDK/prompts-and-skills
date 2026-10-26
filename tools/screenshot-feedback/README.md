# Screenshot Feedback

A macOS menu bar app for showing an AI agent what you mean. Drag an area, mark it up with numbered pins, arrows and boxes, give each mark a note, and paste one path into the chat.

## Known limits

- macOS 13 or later. Built and used on Apple silicon, macOS 26.
- The hotkeys and the apps Done can switch to are fixed in the source (`registerHotKeys()`, `agentApps`).

## Use

| Keys | |
|---|---|
| ⌥⇧4 | Quick shot. Drag an area (Space for a window). Saves the PNG and copies its path. |
| ⌥⇧5 | Mark-up shot. Same capture, then the marking window. **Done** saves the marked PNG and a `.md` note, copies the note's path and switches to Claude (or ChatGPT, or stays put: set in the menu). |

Marking window: Pin `P`, Arrow `A`, Line `L`, Box `B`, Draw `D`, Text `T`, Select `V`, grid `G`. Each mark gets a number and its own note. ⌘Z undoes, ⌘↩ is Done. The menu can also mark up the last quick shot.

Give the agent the `.md`. It names the image and lists each mark with its note and position, the text in the shot, and the app, window and page address that were in front when you pressed the keys.

## Install

```bash
xcode-select --install    # Apple's command line tools, if you don't have them
git clone https://github.com/NWDK/prompts-and-skills
cd prompts-and-skills
bash tools/screenshot-feedback/build.sh --open
```

It installs to `~/Applications`. The first shot asks for Screen Recording: turn it on in System Settings › Privacy & Security › Screen & System Audio Recording, then quit from the menu bar icon and open the app again. The first shot of a Chrome or Safari page asks to read the page address.

Rebuilding asks for both again. Each build is signed on your Mac, so macOS treats it as a new app.

To remove it, quit from the menu and delete the app. Your shots stay where they are.

## In the background

- Starts at login. Toggle it in the menu.
- Shots live in `~/Pictures/Screenshot-Feedback/`. At launch and every six hours the app moves its own expired shots to the Trash: 14 days old in the folder itself, 30 in a project subfolder. It never touches `keep/` or any file without its date-stamped name.
- No network calls. Text in the shot is read on the Mac (Vision).

## How it works

| | Why |
|---|---|
| Capture is macOS's `screencapture -i` | The drag behaves exactly like ⌘⇧4 |
| Hotkeys through Carbon `RegisterEventHotKey` | Works in any app, no Accessibility permission |
| Marks are drawn on a transparent layer, then composited onto the original in Swift | Full-resolution output; the page never reads the screenshot's pixels |
| The `.md` carries its own instructions for the agent | Works with any agent that reads files; nothing to install on that side |
| Cleanup ages: 14 days unused, 30 once filed in a project folder | An unused shot is noise; a filed one may be needed while the work is reviewed. The Trash keeps both recoverable |

## Files and test

`ScreenshotFeedback.swift` is the app, `editor/` the marking window, `make-icon.swift` draws the icon, `build.sh` builds and installs.

```bash
bash tools/screenshot-feedback/test.sh
```

Builds into a scratch folder and checks the cleanup rule against planted files. Leaves your installed copy alone.
