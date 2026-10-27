import Foundation

public enum JSONValue: Codable, Sendable, Equatable {
    case string(String), number(Double), bool(Bool), object([String: JSONValue]), array([JSONValue]), null

    public init(from decoder: Decoder) throws {
        let value = try decoder.singleValueContainer()
        if value.decodeNil() { self = .null }
        else if let item = try? value.decode(Bool.self) { self = .bool(item) }
        else if let item = try? value.decode(String.self) { self = .string(item) }
        else if let item = try? value.decode(Double.self) { self = .number(item) }
        else if let item = try? value.decode([String: JSONValue].self) { self = .object(item) }
        else { self = .array(try value.decode([JSONValue].self)) }
    }
    public func encode(to encoder: Encoder) throws {
        var value = encoder.singleValueContainer()
        switch self {
        case .string(let item): try value.encode(item)
        case .number(let item): try value.encode(item)
        case .bool(let item): try value.encode(item)
        case .object(let item): try value.encode(item)
        case .array(let item): try value.encode(item)
        case .null: try value.encodeNil()
        }
    }
    public var text: String {
        switch self {
        case .string(let item): return item
        case .number(let item): return item.rounded() == item ? String(format: "%.0f", item) : String(item)
        case .bool(let item): return item ? "Yes" : "No"
        default: return ""
        }
    }
    public var object: [String: JSONValue] { if case .object(let item) = self { return item }; return [:] }
}

public struct PackFields: Codable, Sendable, Equatable {
    public var batch = ""
    public var product = ""
    public var brand = ""
    public var mfg = ""
    public var exp = ""
    public var maker = ""
    public var source: String?
    public var confirmed: Bool?
    public init() {}
    public init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        batch = try values.decodeIfPresent(String.self, forKey: .batch) ?? ""
        product = try values.decodeIfPresent(String.self, forKey: .product) ?? ""
        brand = try values.decodeIfPresent(String.self, forKey: .brand) ?? ""
        mfg = try values.decodeIfPresent(String.self, forKey: .mfg) ?? ""
        exp = try values.decodeIfPresent(String.self, forKey: .exp) ?? ""
        maker = try values.decodeIfPresent(String.self, forKey: .maker) ?? ""
        source = try values.decodeIfPresent(String.self, forKey: .source)
        confirmed = try values.decodeIfPresent(Bool.self, forKey: .confirmed)
    }
    public var payload: [String: JSONValue] {
        ["batch": .string(batch), "product": .string(product), "brand": .string(brand), "mfg": .string(mfg), "exp": .string(exp), "maker": .string(maker)]
    }
}

public struct Step: Codable, Identifiable, Sendable {
    public let step: Int?
    public let action: String?
    public let summary: String
    public let source: String?
    public let ms: Double?
    public var id: String { "\(step ?? 0)-\(action ?? summary)" }
}

public struct Citation: Codable, Identifiable, Sendable {
    public let title: String?
    public let source_title: String?
    public let source_url: String?
    public let url: String?
    public let text: String?
    public let list_month: String?
    public let row_no: JSONValue?
    public let synthetic: Bool?
    public var id: String { "\(source_url ?? title ?? "citation")-\(row_no?.text ?? "")-\(text ?? "")" }
    public var link: URL? {
        guard let value = URL(string: source_url ?? url ?? ""), ["https", "http"].contains(value.scheme) else { return nil }
        return value
    }
}

public struct Verdict: Codable, Sendable {
    public let label: String
    public let headline: String
    public let explanation: String
    public let advice: String?
    public let citations: [Citation]?
    public let evidence: [String: String]?
    public let batch_evidence: String?
    public let latest_month: String?
    public let demo: Bool?
}

public struct Pending: Codable, Sendable {
    public let kind: String
    public let question: String
    public let options: [String]?
    public let positions: [Int]?
    public let batch: String?
    public let error: String?
}

public struct CheckSnapshot: Codable, Identifiable, Sendable {
    public let thread_id: String
    public let status: String
    public let fields: PackFields
    public let pending: Pending?
    public let final: Verdict?
    public let history: [Step]?
    public let demo: Bool?
    public let warnings: [String]?
    public let created_at: String?
    public var id: String { thread_id }
}

public struct DemoCase: Codable, Identifiable, Sendable {
    public let id: String
    public let name: String
    public let description: String
    public let synthetic: Bool
}

public struct Record: Codable, Identifiable, Sendable {
    public let values: [String: JSONValue]
    public init(from decoder: Decoder) throws { values = try decoder.singleValueContainer().decode([String: JSONValue].self) }
    public func encode(to encoder: Encoder) throws { var value = encoder.singleValueContainer(); try value.encode(values) }
    public subscript(_ key: String) -> String { values[key]?.text ?? "" }
    public var id: String { self["id"].isEmpty ? self["thread_id"] : self["id"] }
    public var fields: [String: JSONValue] { values["fields"]?.object ?? [:] }
    public var verdict: [String: JSONValue] { values["final"]?.object ?? [:] }
}

public struct Items<Element: Codable & Sendable>: Codable, Sendable {
    public let items: [Element]
    public let total: Int?
    public let pages: Int?
}
