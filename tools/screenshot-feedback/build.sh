#!/bin/bash
# Builds Screenshot Feedback.app and installs it in ~/Applications.
#   bash build.sh          build and install
#   bash build.sh --open   build, install and start it
#   APP_DIR=<folder>       install somewhere other than ~/Applications (tests use this)
#
# Each build is signed afresh on this Mac, so macOS treats it as a new app: on a rebuild this
# clears the old copy's Screen Recording and Automation choices (this app's only) so macOS asks
# again, instead of silently refusing the new copy. Rebuild only when something changed.
set -euo pipefail
# /usr/bin/swiftc exists even without the tools, so ask xcode-select instead.
xcode-select -p >/dev/null 2>&1 || { echo "Apple's command line tools are not installed. Run: xcode-select --install"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
NAME="Screenshot Feedback"
ID="local.screenshot-feedback"
APP="${APP_DIR:-$HOME/Applications}/$NAME.app"
P="$APP/Contents/Info.plist"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT

swiftc -swift-version 5 -O -target "$(uname -m)-apple-macos13.0" -o "$BUILD/ScreenshotFeedback" "$HERE/ScreenshotFeedback.swift"
swift "$HERE/make-icon.swift" "$BUILD/AppIcon.iconset" "$BUILD"   # app icon and menu bar icon
iconutil -c icns "$BUILD/AppIcon.iconset" -o "$BUILD/AppIcon.icns"

# Both steps act on the bundle id, so on every copy: an install elsewhere (APP_DIR) skips them.
if [ -d "$APP" ] && [ -z "${APP_DIR:-}" ]; then
  # Quit the running copy without launching one that isn't running.
  osascript -e "if application id \"$ID\" is running then tell application id \"$ID\" to quit" >/dev/null 2>&1 || true
  # Quitting takes a moment; opening the new copy before the old one has gone just reopens the old.
  for _ in $(seq 25); do pgrep -x ScreenshotFeedback >/dev/null || break; sleep 0.2; done
  tccutil reset ScreenCapture "$ID" >/dev/null 2>&1 || echo "Note: the old Screen Recording choice was not cleared"
  tccutil reset AppleEvents "$ID" >/dev/null 2>&1 || true
fi

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BUILD/ScreenshotFeedback" "$APP/Contents/MacOS/ScreenshotFeedback"
cp -R "$HERE/editor" "$APP/Contents/Resources/editor"
cp "$BUILD/AppIcon.icns" "$BUILD/MenuIcon.png" "$BUILD/MenuIcon@2x.png" "$APP/Contents/Resources/"
plutil -create xml1 "$P"
for kv in "CFBundleIconFile:AppIcon" "CFBundleName:$NAME" "CFBundleDisplayName:$NAME" "CFBundleIdentifier:$ID" "CFBundleExecutable:ScreenshotFeedback" \
          "CFBundlePackageType:APPL" "CFBundleShortVersionString:0.1" "CFBundleVersion:1" "LSMinimumSystemVersion:13.0" \
          "NSPrincipalClass:NSApplication" \
          "NSAppleEventsUsageDescription:Screenshot Feedback reads the page address from Chrome or Safari, so each note says which page a shot came from."; do
  plutil -insert "${kv%%:*}" -string "${kv#*:}" "$P"
done
plutil -insert LSUIElement -bool YES "$P"          # menu bar only, no Dock icon
plutil -insert NSHighResolutionCapable -bool YES "$P"
xattr -cr "$APP"
codesign --force --deep -s - "$APP"                 # signed on this Mac, so it opens without a warning
echo "Installed: $APP"

if [ "${1:-}" = "--open" ]; then open "$APP"; echo "Started. Look for the pencil icon in the menu bar."; fi
