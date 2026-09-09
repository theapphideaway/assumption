import SwiftUI

/// One day, opened from the calendar grid.
struct DayDetailView: View {
    let isoDate: String

    @Environment(AppCoordinator.self) private var coordinator
    @State private var viewModel: DayDetailViewModel?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if let viewModel, let day = viewModel.day {
                    LocalizedTextView(text: day.title, size: 24).fontWeight(.medium)
                    Text(viewModel.dateLine)
                        .font(Typography.data(11))
                        .foregroundStyle(.secondary)
                    FastChipView(fast: day.fast)
                    if let tone = viewModel.toneLine {
                        Text(tone).font(Typography.data(12)).foregroundStyle(.secondary)
                    }
                    if viewModel.hasOtherCommemorations {
                        Divider()
                        ForEach(viewModel.otherCommemorations) { commemoration in
                            LocalizedTextView(text: commemoration.title, size: 15)
                        }
                    }
                    Button("Readings for this day") {
                        coordinator.showReadings(for: day.date)
                    }
                    .font(Typography.ui(14, weight: .medium))
                    .padding(.top, 4)
                } else if let message = viewModel?.message {
                    Text(message).foregroundStyle(.secondary)
                } else {
                    ProgressView()
                }
            }
            .padding(20)
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar { ToolbarItem(placement: .topBarTrailing) { LanguageMenu() } }
        .task {
            if viewModel == nil {
                viewModel = DayDetailViewModel(calendar: coordinator.services.calendar,
                                               isoDate: isoDate)
            }
            await viewModel?.load()
        }
    }
}
