import Foundation
import Observation

@Observable
@MainActor
final class DayDetailViewModel {
    private(set) var day: Day?
    private(set) var message: String?

    private let calendar: CalendarServicing
    private let isoDate: String

    init(calendar: CalendarServicing, isoDate: String) {
        self.calendar = calendar
        self.isoDate = isoDate
    }

    func load() async {
        guard let date = ISODate.date(from: isoDate) else {
            message = "That date could not be read."
            return
        }
        do { day = try await calendar.day(on: date) }
        catch {
            message = (error as? APIError)?.errorDescription ?? "Not loaded."
        }
    }

    /// Both calendars, because a good number of parishioners track Old Style.
    var dateLine: String {
        guard let day else { return "" }
        return "\(day.date) · \(day.julian) O.S."
    }

    var toneLine: String? {
        day?.tone.map { "Tone \($0)" }
    }

    /// Everything beyond the one already shown as the title.
    var otherCommemorations: [Commemoration] {
        Array((day?.commemorations ?? []).dropFirst())
    }

    var hasOtherCommemorations: Bool { !otherCommemorations.isEmpty }
}
