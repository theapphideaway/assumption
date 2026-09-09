import Foundation

/// Resolved days from the parish server.
protocol CalendarServicing: Sendable {
    func today() async throws -> Day
    func day(on date: Date) async throws -> Day
    func days(from start: Date, count: Int) async throws -> [Day]
}

struct CalendarService: CalendarServicing {
    private let client: APIClientProtocol

    init(client: APIClientProtocol) { self.client = client }

    func today() async throws -> Day {
        try await client.get(.today, as: Day.self)
    }

    func day(on date: Date) async throws -> Day {
        try await client.get(.day(ISODate.string(from: date)), as: Day.self)
    }

    func days(from start: Date, count: Int) async throws -> [Day] {
        let page = try await client.get(
            .days(start: ISODate.string(from: start), count: count),
            as: DayPage.self
        )
        return page.results
    }
}

private struct DayPage: Decodable {
    let results: [Day]
}

/// The server speaks plain "YYYY-MM-DD" in the parish timezone.
enum ISODate {
    private static let formatter: DateFormatter = {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .gregorian)
        f.locale = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    static func string(from date: Date) -> String { formatter.string(from: date) }
    static func date(from string: String) -> Date? { formatter.date(from: string) }
}
