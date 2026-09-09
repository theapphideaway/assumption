import SwiftUI

/// The tab shell. Holds no logic beyond binding each tab to its own path.
struct RootView: View {
    @Environment(AppCoordinator.self) private var coordinator

    var body: some View {
        @Bindable var coordinator = coordinator

        TabView(selection: $coordinator.selectedTab) {
            NavigationStack(path: $coordinator.todayPath) {
                TodayView()
                    .navigationDestination(for: TodayRoute.self, destination: destination)
            }
            .tabItem { Label(Tab.today.title, systemImage: Tab.today.systemImage) }
            .tag(Tab.today)

            NavigationStack(path: $coordinator.prayerPath) {
                PrayerRuleView()
                    .navigationDestination(for: PrayerRoute.self, destination: destination)
            }
            .tabItem { Label(Tab.prayers.title, systemImage: Tab.prayers.systemImage) }
            .tag(Tab.prayers)

            NavigationStack(path: $coordinator.calendarPath) {
                CalendarView()
                    .navigationDestination(for: CalendarRoute.self, destination: destination)
            }
            .tabItem { Label(Tab.calendar.title, systemImage: Tab.calendar.systemImage) }
            .tag(Tab.calendar)

            NavigationStack {
                ParishView()
            }
            .tabItem { Label(Tab.parish.title, systemImage: Tab.parish.systemImage) }
            .tag(Tab.parish)
        }
        .tint(LiturgicalPalette.lapis)
    }

    @ViewBuilder
    private func destination(_ route: TodayRoute) -> some View {
        switch route {
        case .readings(let date): ReadingsView(isoDate: date)
        case .announcements: AnnouncementListView()
        }
    }

    @ViewBuilder
    private func destination(_ route: PrayerRoute) -> some View {
        switch route {
        case .document(let id, let date): PrayerReaderView(documentID: id, isoDate: date)
        }
    }

    @ViewBuilder
    private func destination(_ route: CalendarRoute) -> some View {
        switch route {
        case .day(let date): DayDetailView(isoDate: date)
        case .readings(let date): ReadingsView(isoDate: date)
        }
    }
}
