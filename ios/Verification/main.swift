import Foundation
import CoreGraphics
import ImageIO
import StripCheckKit

// Executable contract checks run without XCTest, including command-line-only Macs.
var passed = 0
func verify(_ name: String, _ work: () throws -> Void) rethrows {
    try work(); passed += 1; print("PASS \(name)")
}
func mustThrow(_ work: () throws -> Void) {
    do { try work(); fatalError("Expected an error") } catch { }
}

try verify("paused snapshot decoding") {
    let input = #"{"thread_id":"check-123","status":"waiting","fields":{"batch":"SYN123","product":"Synthetic product","confirmed":false,"source":"ocr"},"pending":{"kind":"confirm_batch","question":"Read the printed batch","options":["Type the whole batch","Can't tell"],"positions":[1,2]},"history":[{"step":1,"action":"search_exact","source":"rules","summary":"Checked loaded records.","ms":0.1}],"final":null,"demo":true}"#
    let value = try JSONDecoder().decode(CheckSnapshot.self, from: Data(input.utf8))
    precondition(value.pending?.kind == "confirm_batch" && value.fields.batch == "SYN123" && value.fields.maker == "" && value.final == nil)
}
try verify("result and source decoding") {
    let input = #"{"thread_id":"demo-123","status":"done","fields":{"batch":"SYN123"},"final":{"label":"FLAGGED","headline":"Demo result","explanation":"Synthetic fixture only.","citations":[{"title":"Synthetic fixture","source_url":"","row_no":1,"synthetic":true}],"evidence":{"batch":"exact"},"demo":true},"history":[]}"#
    let value = try JSONDecoder().decode(CheckSnapshot.self, from: Data(input.utf8))
    precondition(value.final?.citations?.first?.row_no?.text == "1" && value.final?.citations?.first?.link == nil)
}
try verify("local HTTP and HTTPS address policy") {
    for address in ["http://localhost:8000", "http://192.168.1.12:8000", "http://computer.local:8000", "http://10.0.0.3:8000", "https://stripcheck.example"] { _ = try APIClient(address: address) }
    for address in ["http://public.example", "http://192.168.300.1", "http://127.0.0.1.evil.example", "http://10.x.0.0.1", "ftp://localhost", "https://user:secret@example.com", "https://example.com?k=secret", "javascript:alert(1)"] { mustThrow { _ = try APIClient(address: address) } }
}
try verify("JSON negotiation and private token header") {
    let api = try APIClient(address: "http://localhost:8000", token: "synthetic-token")
    let request = try api.request(path: "/api/checks", method: "POST", body: ["fields": .object(["batch": .string("SYN123")])])
    precondition(request.url?.absoluteString == "http://localhost:8000/api/checks")
    precondition(request.value(forHTTPHeaderField: "Accept") == "application/json")
    precondition(request.value(forHTTPHeaderField: "X-StripCheck-Key") == "synthetic-token" && request.httpMethod == "POST")
    let value = try JSONDecoder().decode(JSONValue.self, from: request.httpBody!)
    precondition(value.object["fields"]?.object["batch"]?.text == "SYN123")
}
try verify("multipart image and resume routing") {
    let api = try APIClient(address: "http://localhost:8000")
    let request = try api.multipart(path: "/api/checks/check-123/resume", jpeg: Data([0xff, 0xd8, 0xff]))
    precondition(request.url?.path == "/api/checks/check-123/resume")
    precondition(request.value(forHTTPHeaderField: "Content-Type")?.contains("multipart/form-data; boundary=StripCheck-") == true)
    precondition(String(decoding: request.httpBody!, as: UTF8.self).contains("name=\"image\""))
    mustThrow { _ = try api.multipart(path: "/api/checks", jpeg: Data(count: 15 * 1024 * 1024 + 1)) }
}
try verify("search encoding and route boundary") {
    let api = try APIClient(address: "https://example.com")
    let request = try api.request(path: "/api/alerts", query: [.init(name: "q", value: "A & B"), .init(name: "page", value: "2")])
    precondition(URLComponents(url: request.url!, resolvingAgainstBaseURL: false)?.queryItems?.first?.value == "A & B")
    mustThrow { _ = try api.request(path: "https://other.example") }
    mustThrow { _ = try api.request(path: "/api/../private") }
}
try verify("mixed record identifiers and cabinet fields") {
    let input = #"{"items":[{"id":12,"product":"Synthetic"},{"id":"saved-1","fields":{"batch":"SYN123"},"final":{"headline":"Demo result"}}],"total":2}"#
    let value = try JSONDecoder().decode(Items<Record>.self, from: Data(input.utf8))
    precondition(value.items[0].id == "12" && value.items[1].fields["batch"]?.text == "SYN123")
}
verify("typed fields exclude client trust assertions") {
    var fields = PackFields(); fields.batch = "SYN123"; fields.source = "ocr"; fields.confirmed = true
    precondition(fields.payload["batch"] == .string("SYN123") && fields.payload["source"] == nil && fields.payload["confirmed"] == nil)
}
try verify("bounded image downsampling keeps aspect ratio") {
    let context = CGContext(data: nil, width: 4800, height: 1200, bitsPerComponent: 8, bytesPerRow: 4800 * 4, space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    let source = NSMutableData()
    let writer = CGImageDestinationCreateWithData(source, "public.png" as CFString, 1, nil)!
    CGImageDestinationAddImage(writer, context.makeImage()!, nil)
    precondition(CGImageDestinationFinalize(writer))
    let jpeg = try ImagePreparation.jpeg(from: source as Data)
    let image = CGImageSourceCreateWithData(jpeg as CFData, nil)!
    let properties = CGImageSourceCopyPropertiesAtIndex(image, 0, nil)! as NSDictionary
    precondition(properties[kCGImagePropertyPixelWidth] as? Int == 2400)
    precondition(properties[kCGImagePropertyPixelHeight] as? Int == 600)
}
verify("corrupt and oversized photo rejection") {
    mustThrow { _ = try ImagePreparation.jpeg(from: Data([1, 2, 3])) }
    mustThrow { _ = try ImagePreparation.jpeg(from: Data(count: 40 * 1024 * 1024 + 1)) }
}
try verify("pairing credentials never follow redirects") {
    let api = try APIClient(address: "http://localhost:8000", token: "synthetic-token")
    let request = try api.request(path: "/api/health")
    let task = api.session.dataTask(with: request)
    let response = HTTPURLResponse(url: request.url!, statusCode: 302, httpVersion: "HTTP/1.1", headerFields: ["Location": "https://other.example"])!
    var blocked = false
    (api.session.delegate as? URLSessionTaskDelegate)?.urlSession?(api.session, task: task, willPerformHTTPRedirection: response, newRequest: URLRequest(url: URL(string: "https://other.example")!)) { redirected in blocked = redirected == nil }
    precondition(blocked)
}

final class StubProtocol: URLProtocol, @unchecked Sendable {
    static var status = 200
    static var payload = Data()
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        let response = HTTPURLResponse(url: request.url!, statusCode: Self.status, httpVersion: "HTTP/1.1", headerFields: ["Content-Type": "application/json"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Self.payload)
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
let configuration = URLSessionConfiguration.ephemeral
configuration.protocolClasses = [StubProtocol.self]
let stubClient = try APIClient(address: "http://localhost:8000", session: URLSession(configuration: configuration))
StubProtocol.status = 429
StubProtocol.payload = Data(#"{"error":{"message":"Please wait and try again."}}"#.utf8)
do {
    let _: JSONValue = try await stubClient.get("/api/health")
    fatalError("Expected the server error")
} catch APIError.http(let status, let message) {
    precondition(status == 429 && message == "Please wait and try again.")
    passed += 1; print("PASS server error decoding without a network connection")
}
StubProtocol.status = 200
StubProtocol.payload = Data("invalid JSON".utf8)
do {
    let _: JSONValue = try await stubClient.get("/api/health")
    fatalError("Expected malformed response rejection")
} catch APIError.invalidResponse {
    passed += 1; print("PASS malformed server response handling")
}
let cancelled = Task {
    withUnsafeCurrentTask { $0?.cancel() }
    let _: JSONValue = try await stubClient.get("/api/health")
}
do {
    try await cancelled.value
    fatalError("Expected cancellation")
} catch is CancellationError {
    passed += 1; print("PASS canceled tasks are rejected before sending")
}
print("\(passed) native API and resilience checks passed.")

if let address = ProcessInfo.processInfo.environment["STRIPCHECK_TEST_SERVER"] {
    let api = try APIClient(address: address)
    let health: JSONValue = try await api.get("/api/health")
    precondition(health.object["status"]?.text == "ok")
    let demos: Items<DemoCase> = try await api.get("/api/demo/cases")
    precondition(demos.items.count == 11 && demos.items.allSatisfy(\.synthetic))
    let check: CheckSnapshot = try await api.post("/api/demo/checks", body: ["case_id": .string("01")])
    precondition(check.status == "waiting" && check.pending?.kind == "confirm_batch")
    let result = try await api.resume(thread: check.thread_id, answer: ["typed": .string(check.fields.batch)])
    precondition(result.status == "done" && result.final?.label == "FLAGGED" && result.final?.demo == true)
    let saved: Record = try await api.post("/api/cabinet", body: ["thread_id": .string(result.thread_id)])
    let cabinet: Items<Record> = try await api.get("/api/cabinet")
    precondition(cabinet.items.contains { $0.id == saved.id })
    let _: JSONValue = try await api.send(api.request(path: "/api/cabinet/\(saved.id)", method: "DELETE"))
    let history: Items<CheckSnapshot> = try await api.get("/api/checks")
    precondition(history.items.contains { $0.thread_id == result.thread_id })
    let _: Items<Record> = try await api.get("/api/alerts")
    print("PASS live native URLSession: health, 11 demos, confirmation/resume, verdict decoding, cabinet save/read/delete, activity and alerts.")
}
