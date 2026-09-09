import Foundation

/// Every destination the app can push, per tab.
///
/// Routes are values, not views. A view asks the coordinator to navigate; it
/// never constructs a destination itself, which is what keeps navigation
/// testable and views free of wiring.
enum Tab: String, CaseIterable, Identifiable, Hashable {
    case today, prayers, calendar, parish

    var id: String { rawValue }

    var title: String {
        switch self {
        case .today: "Today"
        case .prayers: "Prayers"
        case .calendar: "Calendar"
        case .parish: "Parish"
        }
    }

    var systemImage: String {
        switch self {
        case .today: "sun.horizon"
        case .prayers: "book.closed"
        case .calendar: "calendar"
        case .parish: "building.columns"
        }
    }
}

enum TodayRoute: Hashable {
    case readings(date: String)
    case announcements
}

enum PrayerRoute: Hashable {
    case document(id: String, date: String?)
}

enum CalendarRoute: Hashable {
    case day(date: String)
    case readings(date: String)
}
