import Foundation
import Observation

/// A month of resolved days.
///
/// The server returns a whole window in one call, which doubles as the offline
/// cache — the calendar and the cache are the same request.
@Observable
@MainActor
final class CalendarViewModel {
    enum State { case loading, loaded, failed(String) }

    private(set) var state: State = .loading
    private(set) var days: [String: Day] = [:]
    private(set) var monthStart: Date

    private let calendar: CalendarServicing
    private let gregorian = Calendar(identifier: .gregorian)

    init(calendar: CalendarServicing, reference: Date = Date()) {
        self.calendar = calendar
        var gregorian = Calendar(identifier: .gregorian)
        gregorian.firstWeekday = 1
        let parts = gregorian.dateComponents([.year, .month], from: reference)
        self.monthStart = gregorian.date(from: parts) ?? reference
    }

    func load() async {
        state = .loading
        do {
            let fetched = try await calendar.days(from: monthStart, count: daysInMonth)
            days = Dictionary(fetched.map { ($0.date, $0) }, uniquingKeysWith: { first, _ in first })
            state = .loaded
        } catch {
            state = .failed((error as? APIError)?.errorDescription
                            ?? "The calendar could not be loaded.")
        }
    }

    func step(months: Int) async {
        guard let moved = gregorian.date(byAdding: .month, value: months, to: monthStart)
        else { return }
        monthStart = moved
        await load()
    }

    var daysInMonth: Int {
        gregorian.range(of: .day, in: .month, for: monthStart)?.count ?? 30
    }

    var monthTitle: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "LLLL yyyy"
        return formatter.string(from: monthStart)
    }

    /// Blank cells before the first, so the grid lines up under its weekday row.
    var leadingBlanks: Int {
        (gregorian.component(.weekday, from: monthStart) - gregorian.firstWeekday + 7) % 7
    }

    func day(at index: Int) -> Day? {
        guard let date = gregorian.date(byAdding: .day, value: index, to: monthStart)
        else { return nil }
        return days[ISODate.string(from: date)]
    }
}
