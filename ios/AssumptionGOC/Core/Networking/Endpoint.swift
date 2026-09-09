import Foundation

/// A path on the parish API.
///
/// Every path keeps its TRAILING SLASH. Django redirects without one, so a
/// missing slash silently costs an extra round trip on every single request.
struct Endpoint {
    let path: String
    let query: [URLQueryItem]

    init(_ path: String, query: [URLQueryItem] = []) {
        self.path = path.hasSuffix("/") || path.contains("?") ? path : path + "/"
        self.query = query
    }

    func url(base: URL) -> URL? {
        guard var components = URLComponents(
            url: base.appendingPathComponent(path),
            resolvingAgainstBaseURL: false
        ) else { return nil }
        if !query.isEmpty { components.queryItems = query }
        return components.url
    }
}

extension Endpoint {
    static let today = Endpoint("api/v1/today")
    static let prayers = Endpoint("api/v1/prayers")
    static let announcements = Endpoint("api/v1/announcements")
    static let scriptureBooks = Endpoint("api/v1/scripture/books")

    static func day(_ isoDate: String) -> Endpoint {
        Endpoint("api/v1/day/\(isoDate)")
    }

    static func days(start: String, count: Int) -> Endpoint {
        Endpoint("api/v1/days", query: [
            .init(name: "start", value: start),
            .init(name: "days", value: String(count)),
        ])
    }

    static func prayers(date: String) -> Endpoint {
        Endpoint("api/v1/prayers", query: [.init(name: "date", value: date)])
    }

    static func chapter(book: String, number: Int) -> Endpoint {
        Endpoint("api/v1/scripture/\(book)/\(number)")
    }
}
