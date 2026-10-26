// Screenshot Feedback: a menu bar app for pointing at things on screen when giving an agent feedback.
//
//   ⌥⇧4  Quick shot: drag an area (Space switches to a window). Saved to the feedback folder and
//         its path copied, ready to paste into an agent chat.
//   ⌥⇧5  Mark-up shot: the same capture, then the marking window. Done saves the marked image and a
//         note file beside it, copies the note's path and switches to the agent app chosen in the menu.
//
// Capture is the Mac's own `screencapture`, so the drag feels exactly like ⌘⇧4. Built by build.sh.
import Cocoa
import WebKit
import Carbon.HIToolbox
import UniformTypeIdentifiers
import Vision
import ServiceManagement

// SCREENSHOT_FEEDBACK_FOLDER is a test seam: it points the app at a scratch folder.
let folder = URL(fileURLWithPath: ProcessInfo.processInfo.environment["SCREENSHOT_FEEDBACK_FOLDER"]
                 ?? NSHomeDirectory() + "/Pictures/Screenshot-Feedback", isDirectory: true)
let keepFolder = folder.appendingPathComponent("keep", isDirectory: true)
// After Done, switch to this app (matched by its name, so any agent app can be added). "" stays put.
let agentApps = ["Claude", "ChatGPT"]
var returnTo: String {
  get { UserDefaults.standard.string(forKey: "ReturnTo") ?? "Claude" }
  set { UserDefaults.standard.set(newValue, forKey: "ReturnTo") }
}
// Only files whose names start with this stamp are ever moved by the cleanup: the app's own shots.
let stampPattern = try! NSRegularExpression(pattern: "^\\d{4}-\\d{2}-\\d{2}_\\d{6}_")

struct Source {
  var app = "", bundle = "", window = "", url = "", pageTitle = ""
  var dict: [String: String] { ["app": app, "bundle": bundle, "window": window, "url": url, "pageTitle": pageTitle] }
}

func sanitize(_ s: String) -> String {
  let kept = s.unicodeScalars.map { CharacterSet.alphanumerics.contains($0) ? String($0) : "-" }.joined()
  let collapsed = kept.split(separator: "-").joined(separator: "-")
  return collapsed.isEmpty ? "screen" : String(collapsed.prefix(40))
}

func stamp() -> String {
  let f = DateFormatter(); f.locale = Locale(identifier: "en_AU_POSIX"); f.dateFormat = "yyyy-MM-dd_HHmmss"
  return f.string(from: Date())
}

func copyToClipboard(_ s: String) {
  NSPasteboard.general.clearContents()
  NSPasteboard.general.setString(s, forType: .string)
}

// Read before the capture starts, while the app being captured is still in front.
func frontSource() -> Source {
  var s = Source()
  guard let app = NSWorkspace.shared.frontmostApplication else { return s }
  s.app = app.localizedName ?? ""; s.bundle = app.bundleIdentifier ?? ""
  // Window names are only visible to an app with Screen Recording, which capture needs anyway.
  if let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] {
    for w in list where (w[kCGWindowOwnerPID as String] as? Int32) == app.processIdentifier && (w[kCGWindowLayer as String] as? Int) == 0 {
      if let n = w[kCGWindowName as String] as? String, !n.isEmpty { s.window = n; break }
    }
  }
  let script: String?
  switch s.bundle {
  case "com.google.Chrome": script = "tell application id \"com.google.Chrome\" to return (URL of active tab of front window) & linefeed & (title of active tab of front window)"
  case "com.apple.Safari": script = "tell application id \"com.apple.Safari\" to return (URL of front document) & linefeed & (name of front document)"
  default: script = nil
  }
  if let src = script, let out = NSAppleScript(source: src)?.executeAndReturnError(nil).stringValue {
    let lines = out.components(separatedBy: "\n")
    s.url = lines.first ?? ""; s.pageTitle = lines.dropFirst().joined(separator: " ")
  }
  return s
}

// The screen the pointer ended on: where the drag or the window click finished.
func pointerScreen() -> (name: String, scale: CGFloat) {
  let m = NSEvent.mouseLocation
  let screen = NSScreen.screens.first { NSMouseInRect(m, $0.frame, false) } ?? NSScreen.main
  return (screen?.localizedName ?? "", screen?.backingScaleFactor ?? 2)
}

// The text inside the shot, read on this Mac with the system's own text recognition (Live Text).
// Lines run top to bottom, then left to right.
func shotText(_ url: URL) -> [String] {
  guard let src = CGImageSourceCreateWithURL(url as CFURL, nil), let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { return [] }
  let request = VNRecognizeTextRequest()
  request.recognitionLevel = .accurate
  request.usesLanguageCorrection = true
  try? VNImageRequestHandler(cgImage: img, options: [:]).perform([request])
  let found = (request.results ?? []).compactMap { o -> (CGRect, String)? in
    guard let t = o.topCandidates(1).first?.string, !t.trimmingCharacters(in: .whitespaces).isEmpty else { return nil }
    return (o.boundingBox, t)
  }
  // Vision's origin is bottom-left; a line counts as the same row when its middles are within half a line.
  return found.sorted { a, b in
    let rowGap = abs(a.0.midY - b.0.midY), tol = min(a.0.height, b.0.height) / 2
    return rowGap > tol ? a.0.midY > b.0.midY : a.0.minX < b.0.minX
  }.map { $0.1 }
}

func pixelSize(_ url: URL) -> (Int, Int)? {
  guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
        let props = CGImageSourceCopyPropertiesAtIndex(src, 0, nil) as? [CFString: Any],
        let w = props[kCGImagePropertyPixelWidth] as? Int, let h = props[kCGImagePropertyPixelHeight] as? Int else { return nil }
  return (w, h)
}

// Draws the marks layer (same pixel size, transparent) over the original capture, keeping its colour space.
func composite(raw: URL, overlay: Data, out: URL) -> Bool {
  guard let bs = CGImageSourceCreateWithURL(raw as CFURL, nil), let base = CGImageSourceCreateImageAtIndex(bs, 0, nil),
        let os = CGImageSourceCreateWithData(overlay as CFData, nil), let over = CGImageSourceCreateImageAtIndex(os, 0, nil) else { return false }
  let rect = CGRect(x: 0, y: 0, width: base.width, height: base.height)
  let space = base.colorSpace ?? CGColorSpace(name: CGColorSpace.sRGB)!
  guard let ctx = CGContext(data: nil, width: base.width, height: base.height, bitsPerComponent: 8, bytesPerRow: 0,
                            space: space, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return false }
  ctx.draw(base, in: rect); ctx.draw(over, in: rect)
  guard let img = ctx.makeImage(),
        let dest = CGImageDestinationCreateWithURL(out as CFURL, UTType.png.identifier as CFString, 1, nil) else { return false }
  // Keep the original's DPI, so a Retina shot opens at its real size.
  let props = CGImageSourceCopyPropertiesAtIndex(bs, 0, nil) as? [CFString: Any] ?? [:]
  let dpi = props.filter { $0.key == kCGImagePropertyDPIWidth || $0.key == kCGImagePropertyDPIHeight }
  CGImageDestinationAddImage(dest, img, dpi as CFDictionary)
  return CGImageDestinationFinalize(dest)
}

let folderReadme = """
# Screenshot Feedback shots

Screenshots taken with Screenshot Feedback (⌥⇧4 quick shot, ⌥⇧5 mark-up shot).

- This folder is the inbox. New shots land here as `<date>_<time>_<app>.png`. A mark-up shot also
  has a `.md` note beside it with the note, the numbered marks, the text in the shot and where it
  came from. Point an agent at the `.md`.
- One subfolder per project (for example `my-app/`): shots an agent has used, filed by the
  project they were for.
- `keep/`: anything you want to keep. Nothing in here is ever moved.

## Cleanup (done by the app, on launch and every six hours)

- Shots left in the inbox older than 14 days go to the Trash.
- Shots in a project subfolder older than 30 days go to the Trash.
- Only files whose names start with the app's date stamp are moved, and only ever to the Trash,
  so anything can be put back from there until the Trash is emptied.

## Rules for agents

- Read a shot's `.md` and the image it names. Marks are numbered in the image and listed in the note.
- When the task a shot was for is finished, move that shot (and its `.md`) into a subfolder named
  for the project, in lowercase with hyphens, creating it if needed. Update the `Image:` line in the
  `.md` to the new path. Only the shots you used.
- Never put a shot inside a Git repo: it would get committed. If a shot is worth keeping as a record
  (a bug for developers, a design decision), copy it into the project on purpose.
- Never delete, never empty the Trash, never touch `keep/`.
"""

func ensureFolders() {
  let fm = FileManager.default
  for d in [folder, keepFolder] { try? fm.createDirectory(at: d, withIntermediateDirectories: true) }
  let readme = folder.appendingPathComponent("README.md")
  if !fm.fileExists(atPath: readme.path) { try? folderReadme.write(to: readme, atomically: true, encoding: .utf8) }
}

// Returns what it moved, or with dryRun what it would move.
@discardableResult func cleanUp(dryRun: Bool = false) -> [String] {
  let fm = FileManager.default, now = Date()
  var moved: [String] = []
  func sweep(_ dir: URL, days: Double) {
    guard let items = try? fm.contentsOfDirectory(at: dir, includingPropertiesForKeys: [.contentModificationDateKey, .isRegularFileKey],
                                                  options: [.skipsHiddenFiles]) else { return }
    for u in items {
      let name = u.lastPathComponent
      guard stampPattern.firstMatch(in: name, range: NSRange(name.startIndex..., in: name)) != nil,
            ["png", "md"].contains(u.pathExtension.lowercased()),
            let v = try? u.resourceValues(forKeys: [.contentModificationDateKey, .isRegularFileKey]), v.isRegularFile == true,
            let modified = v.contentModificationDate, now.timeIntervalSince(modified) > days * 86_400 else { continue }
      moved.append(u.path)
      if !dryRun { try? fm.trashItem(at: u, resultingItemURL: nil) }
    }
  }
  sweep(folder, days: 14)   // the inbox: shots nobody used
  // Project subfolders: shots an agent filed after using them. keep/ is never swept, in any case
  // (the Mac's disk ignores case, so Keep/ is the same folder to the user).
  let subfolders = (try? fm.contentsOfDirectory(at: folder, includingPropertiesForKeys: [.isDirectoryKey], options: [.skipsHiddenFiles])) ?? []
  for d in subfolders where (try? d.resourceValues(forKeys: [.isDirectoryKey]))?.isDirectory == true && d.lastPathComponent.lowercased() != "keep" {
    sweep(d, days: 30)
  }
  return moved
}

// Serves the one shot being marked as shot://image, so the page needs no read access outside its own folder.
final class ShotScheme: NSObject, WKURLSchemeHandler {
  let file: URL
  init(_ file: URL) { self.file = file }
  func webView(_ w: WKWebView, start task: WKURLSchemeTask) {
    guard let url = task.request.url, let data = try? Data(contentsOf: file) else { return task.didFailWithError(URLError(.fileDoesNotExist)) }
    task.didReceive(URLResponse(url: url, mimeType: "image/png", expectedContentLength: data.count, textEncodingName: nil))
    task.didReceive(data)
    task.didFinish()
  }
  func webView(_ w: WKWebView, stop task: WKURLSchemeTask) {}
}

// The first of base, base-2, base-3... with neither a .png nor a .md yet, so marking up the same
// quick shot twice never overwrites the first note.
func freeBase(_ base: URL) -> URL {
  let fm = FileManager.default
  var candidate = base, n = 2
  while ["png", "md"].contains(where: { fm.fileExists(atPath: candidate.appendingPathExtension($0).path) }) {
    candidate = URL(fileURLWithPath: base.path + "-\(n)"); n += 1
  }
  return candidate
}

var testMode = false

// The marking window: a local page (editor/index.html) in a WebKit view.
final class Editor: NSObject, WKScriptMessageHandler, WKNavigationDelegate, NSWindowDelegate {
  let window: NSWindow
  let web: WKWebView
  let page = Bundle.main.resourceURL!.appendingPathComponent("editor/index.html")
  let raw: URL, outPNG: URL, outMD: URL, deleteRawAfter: Bool
  var onClose: (() -> Void)?
  var pageLoaded = false, textJSON: String?

  init(raw: URL, outBase: URL, source: Source, screen: (name: String, scale: CGFloat), deleteRawAfter: Bool) {
    self.raw = raw; self.deleteRawAfter = deleteRawAfter
    let base = freeBase(outBase)
    outPNG = base.appendingPathExtension("png"); outMD = base.appendingPathExtension("md")
    let (pw, ph) = pixelSize(raw) ?? (1200, 800)
    let config = WKWebViewConfiguration()
    config.setURLSchemeHandler(ShotScheme(raw), forURLScheme: "shot")
    web = WKWebView(frame: .zero, configuration: config)
    // Open on the screen the shot came from, at the shot's on-screen size, inside 90% of that
    // screen, plus the toolbar and side panel.
    let shotScreen = NSScreen.screens.first { $0.localizedName == screen.name } ?? NSScreen.main ?? NSScreen.screens[0]
    let visible = shotScreen.visibleFrame
    let ptW = CGFloat(pw) / screen.scale, ptH = CGFloat(ph) / screen.scale
    // 980 wide: the narrowest window whose toolbar fits on one line.
    let w = min(max(ptW + 340, 980), visible.width * 0.9), h = min(max(ptH + 110, 600), visible.height * 0.9)
    window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: w, height: h), styleMask: [.titled, .closable, .resizable, .miniaturizable],
                      backing: .buffered, defer: false)
    super.init()
    let meta: [String: Any] = [
      "image": "shot://image", "imagePath": outPNG.path, "notePath": outMD.path,
      "width": pw, "height": ph, "scale": screen.scale, "display": screen.name,
      "source": source.dict, "taken": ISO8601DateFormatter().string(from: Date()),
      "folder": folder.path,
    ]
    let json = String(data: try! JSONSerialization.data(withJSONObject: meta), encoding: .utf8)!
    config.userContentController.add(self, name: "cf")
    config.userContentController.addUserScript(WKUserScript(source: "window.CF_META = \(json);", injectionTime: .atDocumentStart, forMainFrameOnly: true))
    window.title = "Mark up · " + (source.app.isEmpty ? "shot" : source.app)
    window.contentView = web
    window.delegate = self
    window.isReleasedWhenClosed = false
    window.setFrameOrigin(NSPoint(x: visible.midX - window.frame.width / 2, y: visible.midY - window.frame.height / 2))
    web.navigationDelegate = self
    web.loadFileURL(page, allowingReadAccessTo: page.deletingLastPathComponent())
    DispatchQueue.global(qos: .userInitiated).async { [weak self] in
      let lines = shotText(raw)
      let json = String(data: (try? JSONSerialization.data(withJSONObject: lines)) ?? Data("[]".utf8), encoding: .utf8) ?? "[]"
      DispatchQueue.main.async { self?.textJSON = json; self?.deliverText() }
    }
  }

  // The text read can finish before the page has loaded; it is handed over once both are ready.
  func deliverText() {
    guard pageLoaded, let json = textJSON else { return }
    textJSON = nil
    web.evaluateJavaScript("window.cfSetText ? (window.cfSetText(\(json)), 'delivered') : 'no page'") { r, _ in
      if testMode { print("shot text \(r ?? "failed")"); fflush(stdout) }
    }
  }

  func webView(_ w: WKWebView, didFinish n: WKNavigation!) { pageLoaded = true; deliverText() }

  // Only the marking page itself loads here: a dropped file or link must not replace it.
  func webView(_ w: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
    decisionHandler(action.request.url?.standardizedFileURL == page.standardizedFileURL ? .allow : .cancel)
  }

  // macOS 14 and later will not let a menu bar app push itself in front of the app in use, so the
  // window floats above everything until the app becomes active (a click on it, see
  // applicationDidBecomeActive). While a marking window is open the app is a regular one, with a
  // Dock icon and a place in ⌘Tab, so a window that slips behind can always be found.
  func show() {
    NSApp.setActivationPolicy(.regular)
    window.level = .floating
    window.orderFrontRegardless()
    window.makeKey()
    if #available(macOS 14, *) { NSApp.activate() } else { NSApp.activate(ignoringOtherApps: true) }
  }

  func userContentController(_ uc: WKUserContentController, didReceive m: WKScriptMessage) {
    guard let body = m.body as? [String: Any], let type = body["type"] as? String else { return }
    switch type {
    case "cancel": window.close()
    case "done":
      guard let overlay = (body["overlay"] as? String)?.components(separatedBy: ",").last.flatMap({ Data(base64Encoded: $0) }),
            let md = body["md"] as? String else { return fail("The marks could not be read from the page.") }
      ensureFolders()
      guard composite(raw: raw, overlay: overlay, out: outPNG) else { return fail("The marked image could not be saved.") }
      do { try md.write(to: outMD, atomically: true, encoding: .utf8) } catch { return fail("The note could not be saved: \(error.localizedDescription)") }
      copyToClipboard(outMD.path)
      window.close()
      if !returnTo.isEmpty { NSWorkspace.shared.runningApplications.first { $0.localizedName == returnTo }?.activate() }
    default: break
    }
  }

  func fail(_ message: String) {
    let a = NSAlert(); a.messageText = "Screenshot Feedback"; a.informativeText = message; a.runModal()
  }

  func windowWillClose(_ n: Notification) {
    web.configuration.userContentController.removeScriptMessageHandler(forName: "cf")
    if deleteRawAfter { try? FileManager.default.removeItem(at: raw) }
    onClose?()
  }
}

final class AppDelegate: NSObject, NSApplicationDelegate, NSMenuDelegate {
  var statusItem: NSStatusItem!
  var editors: [Editor] = []
  var busy = false
  var lastQuickShot: URL?
  var lastQuickScreen: (name: String, scale: CGFloat) = ("", 2)
  var loginItem: NSMenuItem!

  func applicationDidFinishLaunching(_ n: Notification) {
    ensureFolders()
    cleanUp()
    Timer.scheduledTimer(withTimeInterval: 6 * 3600, repeats: true) { _ in cleanUp() }
    statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    let icon = Bundle.main.image(forResource: "MenuIcon")   // drawn by make-icon.swift; template, so it follows the menu bar's colour
    icon?.isTemplate = true
    icon?.size = NSSize(width: 18, height: 18)
    icon?.accessibilityDescription = "Screenshot Feedback"
    statusItem.button?.image = icon
    let menu = NSMenu()
    func item(_ title: String, _ action: Selector, _ key: String = "") -> NSMenuItem {
      let i = NSMenuItem(title: title, action: action, keyEquivalent: key); i.target = self
      if !key.isEmpty { i.keyEquivalentModifierMask = [.option, .shift] }
      return i
    }
    menu.addItem(item("Quick shot", #selector(quickShot), "4"))
    menu.addItem(item("Mark-up shot", #selector(markupShot), "5"))
    menu.addItem(item("Mark up the last quick shot", #selector(markupLast)))
    let after = NSMenuItem(title: "After Done, switch to", action: nil, keyEquivalent: "")
    let choices = NSMenu()
    for name in agentApps + [""] {
      let c = item(name.isEmpty ? "Stay where I am" : name, #selector(chooseReturn(_:)))
      c.representedObject = name
      choices.addItem(c)
    }
    after.submenu = choices
    menu.addItem(after)
    menu.addItem(.separator())
    menu.addItem(item("Open the feedback folder", #selector(openFolder)))
    menu.addItem(item("Clean up now", #selector(cleanNow)))
    loginItem = item("Start at login", #selector(toggleLogin))
    menu.addItem(loginItem)
    menu.addItem(.separator())
    menu.addItem(item("Quit Screenshot Feedback", #selector(quit)))
    statusItem.menu = menu
    menu.delegate = self
    registerHotKeys()
    // Check that the marking window opens in front of the app in use, without a capture or any
    // permission: ScreenshotFeedback --test-markup <image.png> opens it after a pause and prints the
    // shot's size as the page sees it; Done saves to the temporary folder, never the feedback folder.
    if CommandLine.arguments.count == 3, CommandLine.arguments[1] == "--test-markup" {
      testMode = true
      var source = Source(); source.app = "Test"
      DispatchQueue.main.asyncAfter(deadline: .now() + 4) {
        self.openEditor(raw: URL(fileURLWithPath: CommandLine.arguments[2]),
                        outBase: FileManager.default.temporaryDirectory.appendingPathComponent("screenshot-feedback-test"),
                        source: source, screen: pointerScreen(), deleteRawAfter: false)
      }
      DispatchQueue.main.asyncAfter(deadline: .now() + 7) {
        self.editors.last?.web.evaluateJavaScript("(() => { const i = document.getElementById('shot'); return i.naturalWidth + ' x ' + i.naturalHeight })()") { r, _ in
          print("page sees the shot at \(r ?? "nothing")"); fflush(stdout)
        }
      }
    }
    // The hotkeys only work while the app runs, so it starts at login unless switched off in the menu.
    if !UserDefaults.standard.bool(forKey: "LoginItemOffered") {
      UserDefaults.standard.set(true, forKey: "LoginItemOffered")
      try? SMAppService.mainApp.register()
    }
  }

  func capture(to url: URL, done: @escaping (Bool) -> Void) {
    guard !busy else { return }
    busy = true
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    p.arguments = ["-i", "-o", url.path]   // -i: drag an area, Space for a window, Esc cancels. -o: no window shadow.
    p.terminationHandler = { _ in
      DispatchQueue.main.async {
        self.busy = false
        done(FileManager.default.fileExists(atPath: url.path))
      }
    }
    do { try p.run() } catch { busy = false; done(false) }
  }

  @objc func quickShot() {
    ensureFolders()
    let source = frontSource()
    let url = folder.appendingPathComponent("\(stamp())_\(sanitize(source.app)).png")
    capture(to: url) { ok in
      guard ok else { return }
      self.lastQuickShot = url
      self.lastQuickScreen = pointerScreen()
      copyToClipboard(url.path)
    }
  }

  @objc func markupShot() {
    let source = frontSource()
    let base = folder.appendingPathComponent("\(stamp())_\(sanitize(source.app))")
    let raw = FileManager.default.temporaryDirectory.appendingPathComponent("screenshot-feedback-\(UUID().uuidString).png")
    capture(to: raw) { ok in
      guard ok else { return }
      self.openEditor(raw: raw, outBase: base, source: source, screen: pointerScreen(), deleteRawAfter: true)
    }
  }

  @objc func markupLast() {
    guard let shot = lastQuickShot, FileManager.default.fileExists(atPath: shot.path) else {
      let a = NSAlert(); a.messageText = "No quick shot yet"; a.informativeText = "Take a quick shot with ⌥⇧4 first."; a.runModal(); return
    }
    // The quick shot stays as it was; the marked copy sits beside it as <name>-marked.png and .md.
    var source = Source()
    source.app = shot.deletingPathExtension().lastPathComponent.components(separatedBy: "_").dropFirst(2).joined(separator: "_")
    openEditor(raw: shot, outBase: URL(fileURLWithPath: shot.deletingPathExtension().path + "-marked"),
               source: source, screen: lastQuickScreen, deleteRawAfter: false)
  }

  func openEditor(raw: URL, outBase: URL, source: Source, screen: (name: String, scale: CGFloat), deleteRawAfter: Bool) {
    let e = Editor(raw: raw, outBase: outBase, source: source, screen: screen, deleteRawAfter: deleteRawAfter)
    e.onClose = { [weak self, weak e] in
      self?.editors.removeAll { $0 === e }
      if self?.editors.isEmpty == true { NSApp.setActivationPolicy(.accessory) }   // back to the menu bar only
    }
    editors.append(e)
    e.show()
  }

  // Once the app is in front, marking windows behave like ordinary windows again.
  func applicationDidBecomeActive(_ n: Notification) { editors.forEach { $0.window.level = .normal } }

  @objc func openFolder() { ensureFolders(); NSWorkspace.shared.open(folder) }
  @objc func cleanNow() { cleanUp() }
  @objc func quit() { NSApp.terminate(nil) }
  @objc func chooseReturn(_ sender: NSMenuItem) { returnTo = sender.representedObject as? String ?? "" }
  // Tick the current choice each time the menu opens.
  @objc func toggleLogin() {
    let service = SMAppService.mainApp
    do { if service.status == .enabled { try service.unregister() } else { try service.register() } }
    catch { let a = NSAlert(); a.messageText = "Start at login"; a.informativeText = error.localizedDescription; a.runModal() }
  }
  func menuWillOpen(_ menu: NSMenu) {
    loginItem.state = SMAppService.mainApp.status == .enabled ? .on : .off
    menu.items.first { $0.submenu != nil }?.submenu?.items.forEach { $0.state = ($0.representedObject as? String) == returnTo ? .on : .off }
  }

  // Global hotkeys through Carbon: they work in any app and need no Accessibility permission.
  func registerHotKeys() {
    var spec = EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed))
    InstallEventHandler(GetApplicationEventTarget(), { _, event, _ in
      var id = EventHotKeyID()
      GetEventParameter(event, EventParamName(kEventParamDirectObject), EventParamType(typeEventHotKeyID), nil,
                        MemoryLayout<EventHotKeyID>.size, nil, &id)
      DispatchQueue.main.async {
        guard let app = NSApp.delegate as? AppDelegate else { return }
        if id.id == 1 { app.quickShot() } else if id.id == 2 { app.markupShot() }
      }
      return noErr
    }, 1, &spec, nil, nil)
    let signature = OSType(0x43464231) // "CFB1"
    for (id, key) in [(UInt32(1), kVK_ANSI_4), (UInt32(2), kVK_ANSI_5)] {
      var ref: EventHotKeyRef?
      RegisterEventHotKey(UInt32(key), UInt32(optionKey | shiftKey), EventHotKeyID(signature: signature, id: id),
                          GetApplicationEventTarget(), 0, &ref)
    }
  }
}

// Windowless check of the real compositing code: ScreenshotFeedback --composite <raw.png> <layer.png> <out.png>
if CommandLine.arguments.count == 5, CommandLine.arguments[1] == "--composite" {
  let a = CommandLine.arguments
  let ok = (try? Data(contentsOf: URL(fileURLWithPath: a[3]))).map { composite(raw: URL(fileURLWithPath: a[2]), overlay: $0, out: URL(fileURLWithPath: a[4])) } ?? false
  print(ok ? "composited" : "failed"); exit(ok ? 0 : 1)
}

// Windowless check of the login item: ScreenshotFeedback --login-status
if CommandLine.arguments.count == 2, CommandLine.arguments[1] == "--login-status" {
  let st = SMAppService.mainApp.status
  print([SMAppService.Status.notRegistered: "not registered", .enabled: "enabled", .requiresApproval: "requires approval in System Settings", .notFound: "not found"][st] ?? "unknown")
  exit(0)
}

// Windowless check of the text reading: ScreenshotFeedback --text <image.png>
if CommandLine.arguments.count == 3, CommandLine.arguments[1] == "--text" {
  shotText(URL(fileURLWithPath: CommandLine.arguments[2])).forEach { print($0) }; exit(0)
}

// Windowless check of the cleanup rule: lists what it would move to the Trash, moves nothing.
if CommandLine.arguments.count == 2, CommandLine.arguments[1] == "--clean-up-dry-run" {
  cleanUp(dryRun: true).forEach { print($0) }; exit(0)
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
// Shown only while a marking window is open. The Edit menu is what makes copy, paste and select
// all work in the note box; the page handles ⌘Z for marks itself and stops it reaching the menu.
let mainMenu = NSMenu()
for (title, items) in [("Screenshot Feedback", [("Quit Screenshot Feedback", "terminate:", "q")]),
                       ("Edit", [("Undo", "undo:", "z"), ("Redo", "redo:", "Z"), ("Cut", "cut:", "x"),
                                 ("Copy", "copy:", "c"), ("Paste", "paste:", "v"), ("Select All", "selectAll:", "a")])] {
  let top = NSMenuItem(); let sub = NSMenu(title: title)
  items.forEach { sub.addItem(withTitle: $0.0, action: Selector($0.1), keyEquivalent: $0.2) }
  top.submenu = sub; mainMenu.addItem(top)
}
app.mainMenu = mainMenu
app.setActivationPolicy(.accessory)
app.run()
