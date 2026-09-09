import SwiftUI

/// The daily companion screen.
///
/// The glance — fast, tone, both dates — compresses into one header band so the
/// practice can own the body of the screen.
struct TodayView: View {
    @Environment(AppCoordinator.self) private var coordinator
    @State private var viewModel: TodayViewModel?

    var body: some View {
        Group {
            if let viewModel {
                content(viewModel)
            } else {
                ProgressView()
            }
        }
        .navigationTitle("Today")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar { ToolbarItem(placement: .topBarTrailing) { LanguageMenu() } }
        .task {
            if viewModel == nil { viewModel = coordinator.makeTodayViewModel() }
            await viewModel?.load()
        }
    }

    @ViewBuilder
    private func content(_ viewModel: TodayViewModel) -> some View {
        switch viewModel.state {
        case .loading:
            ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
        case .failed(let message):
            ContentUnavailableView("Not loaded", systemImage: "wifi.exclamationmark",
                                   description: Text(message))
        case .loaded:
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    DayHeaderView(viewModel: viewModel)
                    if let document = viewModel.suggestedDocument {
                        PrayerPromptCard(greeting: viewModel.greeting, document: document) {
                            coordinator.showPrayerDocument(id: document.id)
                        }
                    }
                    if viewModel.hasReadings, let day = viewModel.day {
                        ReadingPreviewCard(greek: viewModel.greekReadings,
                                           common: viewModel.commonReadings) {
                            coordinator.showReadings(for: day.date)
                        }
                    }
                    if let announcement = viewModel.latestAnnouncement {
                        AnnouncementCard(announcement: announcement) {
                            coordinator.showAnnouncements()
                        }
                    }
                    if !viewModel.services.isEmpty {
                        ServiceTimesCard(services: viewModel.services)
                    }
                }
                .padding(20)
            }
            .refreshable { await viewModel.load() }
        }
    }
}
