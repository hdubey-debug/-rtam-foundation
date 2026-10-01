// Foreground ("lift subject") masks with Apple's Vision framework. Runs on-device; nothing is downloaded.
// usage: swift subject_mask.swift input.png out_prefix
//   writes <prefix>-all.png (soft matte of every foreground instance, 8-bit) and <prefix>-labels.png (instance ids: 0 = background)
import Vision
import AppKit
import CoreImage

let args = CommandLine.arguments
let inURL = URL(fileURLWithPath: args[1]); let prefix = args[2]
guard let nsimg = NSImage(contentsOf: inURL) else { print("cannot read"); exit(1) }
var rect = CGRect(origin: .zero, size: nsimg.size)
guard let cg = nsimg.cgImage(forProposedRect: &rect, context: nil, hints: nil) else { print("no cgimage"); exit(1) }
let handler = VNImageRequestHandler(cgImage: cg, options: [:])
let req = VNGenerateForegroundInstanceMaskRequest()
do { try handler.perform([req]) } catch { print("vision error: \(error)"); exit(2) }
guard let obs = req.results?.first else { print("NO FOREGROUND FOUND"); exit(3) }
print("instances:", obs.allInstances.map { $0 })
let ctx = CIContext(options: nil)
func save(_ pb: CVPixelBuffer, _ path: String) {
    let ci = CIImage(cvPixelBuffer: pb)
    let cs = CGColorSpace(name: CGColorSpace.linearGray)!
    guard let out = ctx.createCGImage(ci, from: ci.extent, format: .L8, colorSpace: cs) else { print("render fail"); return }
    let rep = NSBitmapImageRep(cgImage: out)
    try? rep.representation(using: .png, properties: [:])?.write(to: URL(fileURLWithPath: path))
    print("wrote", path, out.width, "x", out.height)
}
do {
    let all = try obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler)
    save(all, prefix + "-all.png")
    for i in obs.allInstances {
        let one = try obs.generateScaledMaskForImage(forInstances: IndexSet(integer: i), from: handler)
        save(one, prefix + "-inst\(i).png")
    }
} catch { print("mask error: \(error)"); exit(4) }
