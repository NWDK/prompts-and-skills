// Draws the app icon and the menu bar icon: a capture frame with a pencil writing inside it.
//   swift make-icon.swift <folder>.iconset <folder>    then: iconutil -c icns <folder>.iconset
// The second folder gets MenuIcon.png and MenuIcon@2x.png, used as a template image in the menu bar.
import Cocoa

let iconset = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
let menuDir = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
try? FileManager.default.createDirectory(at: iconset, withIntermediateDirectories: true)

func hex(_ v: Int) -> CGColor {
  CGColor(srgbRed: CGFloat((v >> 16) & 255) / 255, green: CGFloat((v >> 8) & 255) / 255, blue: CGFloat(v & 255) / 255, alpha: 1)
}

// The glyph, on a 256 grid with y pointing down. The frame spans 36 to 220; strokes are 14 wide.
func drawGlyph(_ c: CGContext, ink: CGColor) {
  c.setStrokeColor(ink); c.setFillColor(ink)
  c.setLineCap(.round); c.setLineJoin(.round)

  // Four corner brackets: the capture frame.
  let frame = CGMutablePath()
  for (corner, a, b) in [(CGPoint(x: 36, y: 36), CGPoint(x: 36, y: 82), CGPoint(x: 82, y: 36)),
                         (CGPoint(x: 220, y: 36), CGPoint(x: 174, y: 36), CGPoint(x: 220, y: 82)),
                         (CGPoint(x: 220, y: 220), CGPoint(x: 220, y: 174), CGPoint(x: 174, y: 220)),
                         (CGPoint(x: 36, y: 220), CGPoint(x: 82, y: 220), CGPoint(x: 36, y: 174))] {
    frame.move(to: a)
    frame.addArc(tangent1End: corner, tangent2End: b, radius: 12)
    frame.addLine(to: b)
  }
  c.addPath(frame); c.setLineWidth(14); c.strokePath()

  // The stroke and the pencil, nudged left so they sit centred between the frame's sides.
  c.saveGState()
  c.translateBy(x: -5.2, y: 0)

  // The stroke the pencil has just drawn.
  let wave = CGMutablePath()
  wave.move(to: CGPoint(x: 68, y: 174))
  wave.addCurve(to: CGPoint(x: 91, y: 174), control1: CGPoint(x: 76, y: 162), control2: CGPoint(x: 85, y: 162))
  wave.addCurve(to: CGPoint(x: 112, y: 174), control1: CGPoint(x: 97, y: 186), control2: CGPoint(x: 106, y: 186))
  c.addPath(wave); c.setLineWidth(12); c.strokePath()

  // The pencil, drawn pointing left with its tip at the origin, then turned 45° up to the right.
  c.saveGState()
  c.translateBy(x: 116, y: 162); c.rotate(by: -.pi / 4); c.scaleBy(x: 0.62, y: 0.62)
  let body = CGMutablePath()
  body.move(to: .zero)
  body.addLine(to: CGPoint(x: 44, y: -22)); body.addLine(to: CGPoint(x: 156, y: -22))
  body.addArc(center: CGPoint(x: 156, y: 0), radius: 22, startAngle: -.pi / 2, endAngle: .pi / 2, clockwise: false)
  body.addLine(to: CGPoint(x: 44, y: 22)); body.closeSubpath()
  // A gap around the pencil where it crosses the frame.
  c.setBlendMode(.clear)
  c.addPath(body); c.setLineWidth(40); c.drawPath(using: .fillStroke)
  c.setBlendMode(.normal)
  let lines = CGMutablePath()
  lines.addPath(body)
  lines.move(to: CGPoint(x: 44, y: -22)); lines.addLine(to: CGPoint(x: 44, y: 22))     // where the wood meets the tip
  lines.move(to: CGPoint(x: 136, y: -22)); lines.addLine(to: CGPoint(x: 136, y: 22))   // the band before the eraser
  c.addPath(lines); c.setLineWidth(22); c.strokePath()
  let lead = CGMutablePath()
  lead.move(to: .zero); lead.addLine(to: CGPoint(x: 16, y: -8)); lead.addLine(to: CGPoint(x: 16, y: 8)); lead.closeSubpath()
  c.addPath(lead); c.setLineWidth(6); c.drawPath(using: .fillStroke)
  c.restoreGState()
  c.restoreGState()
}

// A transparent square bitmap of px pixels, with a y-down coordinate system of `units` per side.
func bitmap(_ px: Int, units: CGFloat, draw: (CGContext) -> Void) -> CGImage {
  let c = CGContext(data: nil, width: px, height: px, bitsPerComponent: 8, bytesPerRow: 0,
                    space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
  c.translateBy(x: 0, y: CGFloat(px)); c.scaleBy(x: CGFloat(px) / units, y: -CGFloat(px) / units)
  draw(c)
  return c.makeImage()!
}

func png(_ img: CGImage, _ url: URL) {
  let rep = NSBitmapImageRep(cgImage: img)
  try! rep.representation(using: .png, properties: [:])!.write(to: url)
}

// App icon: the glyph in light grey on a dark rounded square, on the macOS 1024 grid (an 824 body).
func appIcon(_ px: Int) -> CGImage {
  let glyph = bitmap(px, units: 256) { drawGlyph($0, ink: hex(0xf2f2f4)) }
  return bitmap(px, units: 1024) { c in
    let body = CGPath(roundedRect: CGRect(x: 100, y: 100, width: 824, height: 824), cornerWidth: 185, cornerHeight: 185, transform: nil)
    c.saveGState(); c.addPath(body); c.clip()
    let gradient = CGGradient(colorsSpace: nil, colors: [hex(0x2a2a2d), hex(0x1c1c1e)] as CFArray, locations: [0, 1])!
    c.drawLinearGradient(gradient, start: CGPoint(x: 0, y: 100), end: CGPoint(x: 0, y: 924), options: [])
    c.restoreGState()
    c.addPath(body); c.setStrokeColor(hex(0x3a3a3e)); c.setLineWidth(4); c.strokePath()
    // The glyph's 256 grid scaled to 614 and centred. Undo the y flip for the draw.
    c.saveGState(); c.translateBy(x: 205, y: 819); c.scaleBy(x: 1, y: -1)
    c.draw(glyph, in: CGRect(x: 0, y: 0, width: 614, height: 614))
    c.restoreGState()
  }
}

for (name, px) in [("16x16", 16), ("16x16@2x", 32), ("32x32", 32), ("32x32@2x", 64), ("128x128", 128),
                   ("128x128@2x", 256), ("256x256", 256), ("256x256@2x", 512), ("512x512", 512), ("512x512@2x", 1024)] {
  png(appIcon(px), iconset.appendingPathComponent("icon_\(name).png"))
}

// Menu bar: black glyph, cropped to the frame and its stroke (29 to 227) so it fills an 18 point square.
for (suffix, px) in [("", 18), ("@2x", 36)] {
  png(bitmap(px, units: 198) { c in c.translateBy(x: -29, y: -29); drawGlyph(c, ink: hex(0x000000)) },
      menuDir.appendingPathComponent("MenuIcon\(suffix).png"))
}
