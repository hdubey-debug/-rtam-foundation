import CoreImage
import Foundation
let msg = CommandLine.arguments[1]
let level = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "Q"
let f = CIFilter(name: "CIQRCodeGenerator")!
f.setValue(msg.data(using: .utf8), forKey: "inputMessage")
f.setValue(level, forKey: "inputCorrectionLevel")
let img = f.outputImage!
let ctx = CIContext(options: nil)
let cg = ctx.createCGImage(img, from: img.extent)!
let w = cg.width, h = cg.height
var data = [UInt8](repeating: 255, count: w*h)
let b = CGContext(data: &data, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w, space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue)!
b.interpolationQuality = .none
b.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
for y in 0..<h { var s = ""; for x in 0..<w { s += data[y*w+x] < 128 ? "1" : "0" }; print(s) }
