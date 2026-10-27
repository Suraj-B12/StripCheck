import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

public enum APIError: Error, LocalizedError, Equatable {
    case invalidAddress, http(Int, String), invalidResponse, imageTooLarge
    public var errorDescription: String? {
        switch self {
        case .invalidAddress: return "Enter an HTTPS address or the local computer address shown in StripCheck's pairing settings."
        case .http(_, let message): return message
        case .invalidResponse: return "The server returned an unreadable response. Check its address and try again."
        case .imageTooLarge: return "Choose a smaller photo. Images must be under 15 MB."
        }
    }
}

public struct APIClient: Sendable {
    public let baseURL: URL
    public let token: String
    public let session: URLSession
    public init(address: String, token: String = "", session: URLSession? = nil) throws {
        guard let url = URL(string: address.trimmingCharacters(in: .whitespacesAndNewlines)),
              let host = url.host, url.user == nil, url.password == nil, url.query == nil, url.fragment == nil,
              url.scheme == "https" || (url.scheme == "http" && Self.isLocalHost(host)) else { throw APIError.invalidAddress }
        self.baseURL = url
        self.token = token
        self.session = session ?? URLSession(configuration: .ephemeral, delegate: RedirectBlocker(), delegateQueue: nil)
    }
    public static func isLocalHost(_ host: String) -> Bool {
        if ["localhost", "::1", "[::1]"].contains(host.lowercased()) || host.lowercased().hasSuffix(".local") { return true }
        let labels = host.split(separator: ".", omittingEmptySubsequences: false)
        guard labels.count == 4, labels.allSatisfy({ !$0.isEmpty && $0.allSatisfy { $0 >= "0" && $0 <= "9" } }) else { return false }
        let parts = labels.compactMap { Int($0) }
        guard parts.count == 4, parts.allSatisfy({ (0...255).contains($0) }) else { return false }
        return parts[0] == 127 || parts[0] == 10 || (parts[0] == 192 && parts[1] == 168) || (parts[0] == 172 && (16...31).contains(parts[1])) || (parts[0] == 169 && parts[1] == 254)
    }
    public func request(path: String, method: String = "GET", body: [String: JSONValue]? = nil, query: [URLQueryItem] = []) throws -> URLRequest {
        guard path.hasPrefix("/api/"), !path.contains(".."), !path.contains("?") else { throw APIError.invalidAddress }
        guard var url = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else { throw APIError.invalidAddress }
        url.path = baseURL.path.trimmingCharacters(in: CharacterSet(charactersIn: "/")).isEmpty ? path : baseURL.path.trimmingCharacters(in: CharacterSet(charactersIn: "/")) + path
        if !url.path.hasPrefix("/") { url.path = "/" + url.path }
        url.queryItems = query.isEmpty ? nil : query
        guard let target = url.url else { throw APIError.invalidAddress }
        var request = URLRequest(url: target, timeoutInterval: 90)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if !token.isEmpty { request.setValue(token, forHTTPHeaderField: "X-StripCheck-Key") }
        if let body { request.httpBody = try JSONEncoder().encode(body); request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        return request
    }
    public func multipart(path: String, jpeg: Data) throws -> URLRequest {
        guard jpeg.count <= 15 * 1024 * 1024 else { throw APIError.imageTooLarge }
        var request = try request(path: path, method: "POST")
        let boundary = "StripCheck-\(UUID().uuidString)"
        var body = Data("--\(boundary)\r\nContent-Disposition: form-data; name=\"image\"; filename=\"pack.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n".utf8)
        body.append(jpeg)
        body.append(Data("\r\n--\(boundary)--\r\n".utf8))
        request.httpBody = body
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        return request
    }
    public func send<T: Decodable & Sendable>(_ request: URLRequest, as type: T.Type = T.self) async throws -> T {
        try Task.checkCancellation()
        let (data, response) = try await session.data(for: request)
        try Task.checkCancellation()
        guard let response = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200..<300).contains(response.statusCode) else {
            let value = try? JSONDecoder().decode(JSONValue.self, from: data)
            let message = value?.object["error"]?.object["message"]?.text
            throw APIError.http(response.statusCode, message?.isEmpty == false ? message! : "The request could not complete (\(response.statusCode)).")
        }
        do { return try JSONDecoder().decode(T.self, from: data) }
        catch { throw APIError.invalidResponse }
    }
    public func get<T: Decodable & Sendable>(_ path: String, query: [URLQueryItem] = [], as type: T.Type = T.self) async throws -> T {
        try await send(request(path: path, query: query), as: type)
    }
    public func post<T: Decodable & Sendable>(_ path: String, body: [String: JSONValue] = [:], as type: T.Type = T.self) async throws -> T {
        try await send(request(path: path, method: "POST", body: body), as: type)
    }
    public func check(fields: PackFields) async throws -> CheckSnapshot { try await post("/api/checks", body: ["fields": .object(fields.payload)]) }
    public func photo(_ jpeg: Data, thread: String? = nil) async throws -> CheckSnapshot {
        try await send(multipart(path: thread.map { "/api/checks/\($0)/resume" } ?? "/api/checks", jpeg: jpeg))
    }
    public func resume(thread: String, answer: [String: JSONValue]) async throws -> CheckSnapshot { try await post("/api/checks/\(thread)/resume", body: answer) }
}

private final class RedirectBlocker: NSObject, URLSessionTaskDelegate, @unchecked Sendable {
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Void) {
        // Pairing credentials and pack uploads never follow redirects to another endpoint.
        completionHandler(nil)
    }
}
