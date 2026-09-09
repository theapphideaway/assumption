import SwiftUI

struct ReadingsView: View {
    let isoDate: String

    @Environment(AppCoordinator.self) private var coordinator
    @State private var viewModel: ReadingsViewModel?

    var body: some View {
        Group {
            if let viewModel { content(viewModel) } else { ProgressView() }
        }
        .navigationTitle("Readings")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar { ToolbarItem(placement: .topBarTrailing) { LanguageMenu() } }
        .task {
            if viewModel == nil { viewModel = coordinator.makeReadingsViewModel(date: isoDate) }
            await viewModel?.load()
        }
    }

    @ViewBuilder
    private func content(_ viewModel: ReadingsViewModel) -> some View {
        switch viewModel.state {
        case .loading:
            ProgressView().frame(maxWidth: .infinity, maxHeight: .infinity)
        case .failed(let message):
            ContentUnavailableView("Not loaded", systemImage: "wifi.exclamationmark",
                                   description: Text(message))
        case .loaded:
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    if let title = viewModel.dayTitle {
                        LocalizedTextView(text: title, size: 22).fontWeight(.medium)
                    }
                    if let note = viewModel.unsourcedNote {
                        Text(note)
                            .font(Typography.ui(13))
                            .foregroundStyle(.secondary)
                    }
                    ReadingSectionView(label: "Epistle",
                                       reference: viewModel.epistleReference,
                                       verses: viewModel.epistleVerses)
                    ReadingSectionView(label: "Gospel",
                                       reference: viewModel.gospelReference,
                                       verses: viewModel.gospelVerses)
                    OtherReadingsView(entries: viewModel.entries)
                }
                .padding(20)
            }
        }
    }
}
