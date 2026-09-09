import Foundation
import Observation

/// Everything Today needs, and every decision it makes.
///
/// The view renders what this exposes and computes nothing itself — no date
/// formatting, no slot picking, no deciding whether a card should appear.
@Observable
@MainActor
final class TodayViewModel {
    enum State {
        case loading
        case loaded
        case failed(String)
    }

    private(set) var state: State = .loading
    private(set) var day: Day?
    private(set) var rule: PrayerResponse?
    private(set) var announcements: [Announcement] = []

    private let calendar: CalendarServicing
    private let prayers: PrayerServicing
    private let announcementService: AnnouncementServicing
    private let clock: () -> Date

    init(calendar: CalendarServicing,
         prayers: PrayerServicing,
         announcements: AnnouncementServicing,
         clock: @escaping () -> Date = Date.init) {
        self.calendar = calendar
        self.prayers = prayers
        self.announcementService = announcements
        self.clock = clock
    }

    func load() async {
        state = .loading
        do {
            // Concurrent: the three are independent and Today needs all of them.
            async let day = calendar.today()
            async let rule = prayers.rule(for: nil)
            async let notices = announcementService.recent()
            self.day = try await day
            self.rule = try await rule
            self.announcements = (try? await notices) ?? []
            state = .loaded
        } catch {
            state = .failed((error as? APIError)?.errorDescription
                            ?? "Today could not be loaded.")
        }
    }

    // MARK: - Presentation

    /// The device clock picks the slot, not the server's suggestion. The one
    /// deliberate exception to computing nothing on the client, and safe
    /// because a time-of-day comparison cannot drift between platforms.
    var suggestedSlot: PrayerSlot {
        PrayerSlot.forHour(Calendar.current.component(.hour, from: clock()))
    }

    var suggestedDocument: PrayerDocument? {
        rule?.documents(for: suggestedSlot).first
    }

    var greeting: String {
        switch suggestedSlot {
        case .morning: "Good morning"
        case .hours: "Today"
        case .evening: "Good evening"
        case .compline: "Before sleep"
        }
    }

    /// "WED 9 SEP · 27 AUG O.S." — both calendars, because a good number of
    /// parishioners still track Old Style.
    var dateLine: String {
        guard let day else { return "" }
        let new = Self.shortDate(from: day.date)
        let old = Self.shortDate(from: day.julian)
        return old.isEmpty ? new : "\(new) · \(old) O.S."
    }

    var toneLine: String? {
        guard let tone = day?.tone else { return nil }
        return "TONE \(tone)"
    }

    var seasonColorToken: String { day?.season.color ?? "gold" }

    var hasReadings: Bool {
        day?.readings?.status == .appointed && !(day?.readings?.entries.isEmpty ?? true)
    }

    /// The Greek use is what Assumption reads; the common course reading is
    /// shown alongside where the two differ.
    var greekReadings: [ReadingEntry] {
        day?.readings?.entries.filter { $0.tradition == "greek" } ?? []
    }

    var commonReadings: [ReadingEntry] {
        day?.readings?.entries.filter { $0.tradition == "common" } ?? []
    }

    var latestAnnouncement: Announcement? { announcements.first }

    var services: [ServiceTime] { day?.parish.services ?? [] }

    private static func shortDate(from iso: String) -> String {
        guard let date = ISODate.date(from: iso) else { return "" }
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "EEE d MMM"
        return formatter.string(from: date).uppercased()
    }
}
