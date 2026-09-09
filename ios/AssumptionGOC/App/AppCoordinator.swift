import Foundation
import Observation
import SwiftUI

/// Owns tab selection and one navigation path per tab.
///
/// Each tab keeps its own path so switching tabs preserves where the reader
/// was — going to Calendar and back should not throw away an open prayer.
@Observable
@MainActor
final class AppCoordinator {
    var selectedTab: Tab = .today

    var todayPath = NavigationPath()
    var prayerPath = NavigationPath()
    var calendarPath = NavigationPath()

    let services: ServiceContainer

    init(services: ServiceContainer) {
        self.services = services
    }

    // MARK: - Navigation

    func showReadings(for date: String) {
        switch selectedTab {
        case .calendar: calendarPath.append(CalendarRoute.readings(date: date))
        default: todayPath.append(TodayRoute.readings(date: date))
        }
    }

    func showAnnouncements() {
        todayPath.append(TodayRoute.announcements)
    }

    func showPrayerDocument(id: String, date: String? = nil) {
        selectedTab = .prayers
        prayerPath.append(PrayerRoute.document(id: id, date: date))
    }

    func showDay(_ date: String) {
        calendarPath.append(CalendarRoute.day(date: date))
    }

    func popToRoot(_ tab: Tab) {
        switch tab {
        case .today: todayPath = NavigationPath()
        case .prayers: prayerPath = NavigationPath()
        case .calendar: calendarPath = NavigationPath()
        case .parish: break
        }
    }

    // MARK: - View models
    //
    // Built here so views never construct their own dependencies.

    func makeTodayViewModel() -> TodayViewModel {
        TodayViewModel(calendar: services.calendar,
                       prayers: services.prayers,
                       announcements: services.announcements)
    }

    func makePrayerRuleViewModel() -> PrayerRuleViewModel {
        PrayerRuleViewModel(prayers: services.prayers)
    }

    func makeReadingsViewModel(date: String) -> ReadingsViewModel {
        ReadingsViewModel(prayers: services.prayers, isoDate: date)
    }

    func makeCalendarViewModel() -> CalendarViewModel {
        CalendarViewModel(calendar: services.calendar)
    }
}
