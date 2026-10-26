# Setup: screenshot-feedback

One install, Apple's Command Line Tools. If `xcode-select -p` already prints a folder, you have them.

```bash
xcode-select --install
```

| | What it is | Why it's needed |
|---|---|---|
| **Command Line Tools** | Apple's compilers and build tools, without the full Xcode | `swiftc` builds the app; `swift` runs the script that draws its icon |

Then follow [Install](README.md#install).
