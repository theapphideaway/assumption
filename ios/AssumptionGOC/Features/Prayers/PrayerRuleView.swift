import SwiftUI

struct PrayerRuleView: View {
    @Environment(AppCoordinator.self) private var coordinator
    @State private var viewModel: PrayerRuleViewModel?

    var body: some View {
        Group {
            if let viewModel { content(viewModel) } else { ProgressView() }
        }
        .navigationTitle("Prayers")
        .toolbar { ToolbarItem(placement: .topBarTrailing) { LanguageMenu() } }
        .task {
            if viewModel == nil { viewModel = coordinator.makePrayerRuleViewModel() }
            await viewModel?.load()
        }
    }

    @ViewBuilder
    private func content(_ viewModel: PrayerRuleViewModel) -> some View {
        switch viewModel.state {
        case .loading:
            ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
        case .failed(let message):
            ContentUnavailableView("Not loaded", systemImage: "wifi.exclamationmark",
                                   description: Text(message))
        case .loaded:
            loaded(viewModel)
        }
    }

    private func loaded(_ viewModel: PrayerRuleViewModel) -> some View {
        @Bindable var viewModel = viewModel

        return VStack(spacing: 0) {
            Picker("Time of day", selection: $viewModel.selectedSlot) {
                ForEach(viewModel.slots) { slot in
                    Text(slot.title).tag(slot)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20)
            .padding(.bottom, 8)

            List {
                ForEach(viewModel.documents) { document in
                    PrayerDocumentRow(document: document) {
                        coordinator.showPrayerDocument(id: document.id)
                    }
                }
                if let note = viewModel.unavailableNote {
                    Text(note)
                        .font(Typography.ui(12))
                        .foregroundStyle(.secondary)
                        .listRowSeparator(.hidden)
                }
            }
            .listStyle(.plain)
        }
        .refreshable { await viewModel.load() }
    }
}
