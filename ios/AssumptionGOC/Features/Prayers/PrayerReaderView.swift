import SwiftUI

/// Praying. Chrome recedes: no tab bar decoration, no counters, nothing to do
/// but read.
struct PrayerReaderView: View {
    let documentID: String
    let isoDate: String?

    @Environment(AppCoordinator.self) private var coordinator
    @State private var viewModel: PrayerReaderViewModel?

    var body: some View {
        Group {
            if let viewModel { content(viewModel) } else { ProgressView() }
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar { ToolbarItem(placement: .topBarTrailing) { LanguageMenu() } }
        .task {
            if viewModel == nil {
                viewModel = PrayerReaderViewModel(
                    prayers: coordinator.services.prayers,
                    documentID: documentID,
                    isoDate: isoDate)
            }
            await viewModel?.load()
        }
    }

    @ViewBuilder
    private func content(_ viewModel: PrayerReaderViewModel) -> some View {
        switch viewModel.state {
        case .loading:
            ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
        case .failed(let message):
            ContentUnavailableView("Not available", systemImage: "book.closed",
                                   description: Text(message))
        case .loaded:
            ScrollView {
                BlockListView(blocks: viewModel.blocks)
                    .padding(.horizontal, 22)
                    .padding(.vertical, 16)
            }
            .navigationTitle(viewModel.title)
            .onAppear { UIApplication.shared.isIdleTimerDisabled = viewModel.keepsScreenAwake }
            .onDisappear { UIApplication.shared.isIdleTimerDisabled = false }
        }
    }
}
