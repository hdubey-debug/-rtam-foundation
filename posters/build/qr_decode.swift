// Decode every QR code in an image with Apple Vision. usage: swift qr_decode.swift image.png
import Vision
import AppKit
let img = NSImage(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))!
var rect = CGRect(origin: .zero, size: img.size)
let cg = img.cgImage(forProposedRect: &rect, context: nil, hints: nil)!
let req = VNDetectBarcodesRequest(); req.symbologies = [.qr]
try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
let res = req.results ?? []
if res.isEmpty { print("NO QR FOUND") }
for r in res { print("QR:", r.payloadStringValue ?? "nil") }
