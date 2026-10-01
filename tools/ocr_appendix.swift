import Foundation
import Vision
import AppKit
let args=CommandLine.arguments
for file in args.dropFirst() {
 autoreleasepool {
  do {
   let req=VNRecognizeTextRequest()
   req.recognitionLevel = .accurate
   req.recognitionLanguages = ["en-US"]
   req.usesLanguageCorrection = false
   let handler=VNImageRequestHandler(url: URL(fileURLWithPath:file),options:[:])
   try handler.perform([req])
   let records=(req.results ?? []).compactMap { o -> [String:Any]? in
     guard let c=o.topCandidates(1).first else {return nil}
     return ["text":c.string,"confidence":c.confidence,"box":[o.boundingBox.minX,o.boundingBox.minY,o.boundingBox.width,o.boundingBox.height]]
   }
   let data=try JSONSerialization.data(withJSONObject:records,options:[.prettyPrinted,.sortedKeys])
   try data.write(to:URL(fileURLWithPath:file+".json"))
   print(URL(fileURLWithPath:file).lastPathComponent,records.count)
  } catch { print("ERROR",file,error) }
 }
}
