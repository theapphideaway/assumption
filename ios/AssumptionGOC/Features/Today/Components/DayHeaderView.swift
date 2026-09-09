import SwiftUI

/// The glance: both dates, tone, fast, and the day's title.
struct DayHeaderView: View {
    let viewModel: TodayViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(viewModel.dateLine)
                    .font(Typography.data(11))
                    .foregroundStyle(LiturgicalPalette.color(forToken: viewModel.seasonColorToken))
                Spacer()
                if let tone = viewModel.toneLine {
                    Text(tone)
                        .font(Typography.data(11))
                        .foregroundStyle(.secondary)
                }
            }

            if let day = viewModel.day {
                LocalizedTextView(text: day.title, size: 24)
                    .fontWeight(.medium)

                HStack(spacing: 8) {
                    FastChipView(fast: day.fast)
                    if day.patronal {
                        Text("Patronal Feast")
                            .font(Typography.ui(11, weight: .semibold))
                            .padding(.horizontal, 8).padding(.vertical, 4)
                            .background(LiturgicalPalette.lapis.opacity(0.15), in: .rect(cornerRadius: 3))
                            .foregroundStyle(LiturgicalPalette.lapis)
                    }
                }
            }
        }
    }
}
