import XCTest
@testable import StripCheckKit

final class StripCheckKitTests: XCTestCase {
    func testServerSnapshotWithQuestionDecodes() throws {
        let json = #"{"thread_id":"check-123","status":"waiting","fields":{"batch":"SYN123","product":"Synthetic product","confirmed":false,"source":"ocr"},"pending":{"kind":"confirm_batch","question":"Read the printed batch","options":["Type the whole batch","Can't tell"],"positions":[1,2]},"history":[{"step":1,"action":"search_exact","source":"rules","summary":"Checked loaded records.","ms":0.1}],"final":null,"demo":true}"#
        let check = try JSONDecoder().decode(CheckSnapshot.self, from: Data(json.utf8))
        XCTAssertEqual(check.pending?.kind, "confirm_batch")
        XCTAssertEqual(check.fields.batch, "SYN123")
        XCTAssertEqual(check.fields.maker, "")
        XCTAssertNil(check.final)
    }
    func testRealisticFinalAndCitationDecode() throws {
        let json = #"{"thread_id":"demo-123","status":"done","fields":{"batch":"SYN123"},"final":{"label":"FLAGGED","headline":"Demo result","explanation":"Synthetic fixture only.","citations":[{"title":"Synthetic fixture","source_url":"","row_no":1,"synthetic":true}],"evidence":{"batch":"exact"},"demo":true},"history":[]}"#
        let check = try JSONDecoder().decode(CheckSnapshot.self, from: Data(json.utf8))
        XCTAssertEqual(check.final?.citations?.first?.row_no?.text, "1")
        XCTAssertNil(check.final?.citations?.first?.link)
    }
    func testLocalAddressAndHTTPSPolicy() throws {
        for address in ["http://localhost:8000", "http://192.168.1.12:8000", "http://computer.local:8000", "http://10.0.0.3:8000", "https://stripcheck.example"] { XCTAssertNoThrow(try APIClient(address: address)) }
        for address in ["http://public.example", "http://192.168.300.1", "http://127.0.0.1.evil.example", "http://10.x.0.0.1", "ftp://localhost", "https://user:secret@example.com", "https://example.com?k=secret", "javascript:alert(1)"] { XCTAssertThrowsError(try APIClient(address: address)) }
    }
    func testJSONNegotiationAndTokenNotInURL() throws {
        let api = try APIClient(address: "http://localhost:8000", token: "test-pairing-token")
        let request = try api.request(path: "/api/checks", method: "POST", body: ["fields": .object(["batch": .string("SYN123")])])
        XCTAssertEqual(request.url?.absoluteString, "http://localhost:8000/api/checks")
        XCTAssertEqual(request.value(forHTTPHeaderField: "Accept"), "application/json")
        XCTAssertEqual(request.value(forHTTPHeaderField: "X-StripCheck-Key"), "test-pairing-token")
        XCTAssertEqual(request.httpMethod, "POST")
        let payload = try JSONDecoder().decode(JSONValue.self, from: request.httpBody!)
        XCTAssertEqual(payload.object["fields"]?.object["batch"]?.text, "SYN123")
    }
    func testMultipartUploadAndResumePath() throws {
        let api = try APIClient(address: "http://localhost:8000")
        let request = try api.multipart(path: "/api/checks/check-123/resume", jpeg: Data([0xff, 0xd8, 0xff]))
        XCTAssertEqual(request.url?.path, "/api/checks/check-123/resume")
        XCTAssertTrue(request.value(forHTTPHeaderField: "Content-Type")?.contains("multipart/form-data; boundary=StripCheck-") == true)
        XCTAssertTrue(String(decoding: request.httpBody!, as: UTF8.self).contains("name=\"image\""))
        XCTAssertThrowsError(try api.multipart(path: "/api/checks", jpeg: Data(count: 15 * 1024 * 1024 + 1)))
    }
    func testSearchQueryEncodingAndRouteBoundary() throws {
        let api = try APIClient(address: "https://example.com")
        let request = try api.request(path: "/api/alerts", query: [.init(name: "q", value: "A & B"), .init(name: "page", value: "2")])
        XCTAssertEqual(URLComponents(url: request.url!, resolvingAgainstBaseURL: false)?.queryItems?.first?.value, "A & B")
        XCTAssertThrowsError(try api.request(path: "https://other.example"))
        XCTAssertThrowsError(try api.request(path: "/api/../private"))
    }
    func testCabinetRecordsAllowNumericAndStringIdentifiers() throws {
        let data = Data(#"{"items":[{"id":12,"product":"Synthetic"},{"id":"saved-1","fields":{"batch":"SYN123"},"final":{"headline":"Demo result"}}],"total":2}"#.utf8)
        let records = try JSONDecoder().decode(Items<Record>.self, from: data)
        XCTAssertEqual(records.items[0].id, "12")
        XCTAssertEqual(records.items[1].fields["batch"]?.text, "SYN123")
    }
    func testTypedFieldsPayloadContainsOnlyPrintedDetails() {
        var fields = PackFields(); fields.batch = "SYN123"; fields.source = "ocr"; fields.confirmed = true
        XCTAssertEqual(fields.payload["batch"], .string("SYN123"))
        XCTAssertNil(fields.payload["source"])
        XCTAssertNil(fields.payload["confirmed"])
    }
    func testPhotoPreparationRejectsCorruptOrOversizedInputs() {
        XCTAssertThrowsError(try ImagePreparation.jpeg(from: Data([1, 2, 3])))
        XCTAssertThrowsError(try ImagePreparation.jpeg(from: Data(count: 40 * 1024 * 1024 + 1)))
    }
}
