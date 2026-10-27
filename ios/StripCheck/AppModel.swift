import SwiftUI
import Security

enum TokenStore {
    private static let service = "app.stripcheck.local"
    static func load() -> String {
        let query: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service, kSecAttrAccount as String: "lan-token", kSecReturnData as String: true, kSecMatchLimit as String: kSecMatchLimitOne]
        var result: CFTypeRef?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess, let data = result as? Data else { return "" }
        return String(data: data, encoding: .utf8) ?? ""
    }
    static func save(_ token: String) throws {
        let query: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service, kSecAttrAccount as String: "lan-token"]
        guard !token.isEmpty else {
            let deleted = SecItemDelete(query as CFDictionary)
            guard deleted == errSecSuccess || deleted == errSecItemNotFound else { throw KeychainFailure() }
            return
        }
        let attributes: [String: Any] = [kSecValueData as String: Data(token.utf8), kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly]
        let updated = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        if updated == errSecSuccess { return }
        guard updated == errSecItemNotFound else { throw KeychainFailure() }
        var item = query
        item.merge(attributes) { _, new in new }
        guard SecItemAdd(item as CFDictionary, nil) == errSecSuccess else { throw KeychainFailure() }
    }
    struct KeychainFailure: LocalizedError { var errorDescription: String? { "The pairing token could not be saved in Keychain. Please try again." } }
}

@MainActor
final class AppModel: ObservableObject {
    @Published var address = UserDefaults.standard.string(forKey: "backendAddress") ?? "http://localhost:8000"
    @Published var snapshot: CheckSnapshot?
    @Published var demos: [DemoCase] = []
    @Published var alerts: [Record] = []
    @Published var cabinet: [Record] = []
    @Published var activity: [CheckSnapshot] = []
    @Published var stats: [String: JSONValue] = [:]
    @Published var error: String?
    @Published var notice: String?
    @Published var busy = false
    @Published var selectedTab = 0
    @Published var alertPage = 1
    @Published var alertPages = 1
    private var token = TokenStore.load()
    private var configuredClient: APIClient?
    private var task: Task<Void, Never>?
    private var operationID = UUID()
    private let cacheURL: URL

    init() {
        let folder = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("StripCheck", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        cacheURL = folder.appendingPathComponent("last-check.json")
        if let data = try? Data(contentsOf: cacheURL), let cache = try? JSONDecoder().decode(CachedCheck.self, from: data), cache.address == address { snapshot = cache.snapshot }
    }
    struct CachedCheck: Codable { let address: String; let snapshot: CheckSnapshot }
    var api: APIClient { get throws {
        if let configuredClient { return configuredClient }
        let client = try APIClient(address: address, token: token)
        configuredClient = client
        return client
    } }
    var tokenValue: String { token }
    var latestMonth: String { stats["latest_month"]?.text ?? "Not loaded" }
    var recordCount: String { stats["alerts"]?.text ?? stats["alert_count"]?.text ?? "0" }

    func perform(_ action: @escaping @MainActor (APIClient) async throws -> Void) {
        task?.cancel()
        let identifier = UUID()
        operationID = identifier
        busy = true; error = nil; notice = nil
        let client: APIClient
        do { client = try api } catch { self.error = error.localizedDescription; busy = false; return }
        task = Task {
            defer { if operationID == identifier { busy = false } }
            do { try Task.checkCancellation(); try await action(client) }
            catch is CancellationError { }
            catch let failure as URLError where failure.code == .cancelled { }
            catch { if operationID == identifier { self.error = error.localizedDescription } }
        }
    }
    func cancel() { task?.cancel(); operationID = UUID(); busy = false }
    func saveSettings(address: String, token: String) throws {
        let client = try APIClient(address: address, token: token)
        try TokenStore.save(token)
        if self.address != address {
            snapshot = nil; activity = []; cabinet = []; alerts = []; stats = [:]
            try? FileManager.default.removeItem(at: cacheURL)
        }
        self.address = address.trimmingCharacters(in: .whitespacesAndNewlines); self.token = token; self.configuredClient = client
        UserDefaults.standard.set(self.address, forKey: "backendAddress")
        refresh()
    }
    private func accept(_ value: CheckSnapshot) {
        guard !Task.isCancelled else { return }
        snapshot = value; selectedTab = 0
        activity.removeAll { $0.thread_id == value.thread_id }; activity.insert(value, at: 0)
        if let data = try? JSONEncoder().encode(CachedCheck(address: address, snapshot: value)) {
            do { try data.write(to: cacheURL, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication]) }
            catch { notice = "The check completed, but this device could not cache it. It remains on your server." }
        }
    }
    func refresh() {
        perform { api in
            async let loadedStats: JSONValue = api.get("/api/stats")
            async let loadedDemos: Items<DemoCase> = api.get("/api/demo/cases")
            async let loadedCabinet: Items<Record> = api.get("/api/cabinet")
            async let loadedActivity: Items<CheckSnapshot> = api.get("/api/checks")
            async let loadedAlerts: Items<Record> = api.get("/api/alerts")
            let (s, d, c, h, a) = try await (loadedStats, loadedDemos, loadedCabinet, loadedActivity, loadedAlerts)
            try Task.checkCancellation()
            self.stats = s.object; self.demos = d.items; self.cabinet = c.items; self.activity = h.items
            self.alerts = a.items; self.alertPage = 1; self.alertPages = a.pages ?? 1
        }
    }
    func check(_ fields: PackFields) { perform { api in self.accept(try await api.check(fields: fields)) } }
    func upload(_ jpeg: Data, resume: Bool = false) {
        let thread = resume ? snapshot?.thread_id : nil
        perform { api in self.accept(try await api.photo(jpeg, thread: thread)) }
    }
    func demo(_ id: String) { perform { api in self.accept(try await api.post("/api/demo/checks", body: ["case_id": .string(id)])) } }
    func answer(_ values: [String: JSONValue]) {
        guard let thread = snapshot?.thread_id else { return }
        perform { api in self.accept(try await api.resume(thread: thread, answer: values)) }
    }
    func openCheck(_ id: String) { perform { api in self.accept(try await api.get("/api/checks/\(id)")) } }
    func savePack() {
        guard let check = snapshot else { return }
        perform { api in
            let _: Record = try await api.post("/api/cabinet", body: ["thread_id": .string(check.thread_id)])
            let items: Items<Record> = try await api.get("/api/cabinet")
            try Task.checkCancellation()
            self.cabinet = items.items; self.notice = "Saved to your cabinet on this server."
        }
    }
    func deletePack(_ id: String) {
        perform { api in
            let _: JSONValue = try await api.send(api.request(path: "/api/cabinet/\(id)", method: "DELETE"))
            try Task.checkCancellation()
            self.cabinet.removeAll { $0.id == id }
        }
    }
    func recheckCabinet() {
        perform { api in
            let _: JSONValue = try await api.post("/api/cabinet/recheck")
            let items: Items<Record> = try await api.get("/api/cabinet")
            try Task.checkCancellation()
            self.cabinet = items.items; self.notice = "Cabinet rechecked against the lists currently loaded."
        }
    }
    func searchAlerts(_ query: String, page: Int = 1) {
        perform { api in
            let result: Items<Record> = try await api.get("/api/alerts", query: [URLQueryItem(name: "q", value: query), URLQueryItem(name: "page", value: String(page))])
            try Task.checkCancellation()
            self.alerts = result.items; self.alertPage = page; self.alertPages = result.pages ?? 1
        }
    }
}
