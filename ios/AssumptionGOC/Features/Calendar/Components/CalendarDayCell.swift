import SwiftUI

/// One day in the month grid.
///
/// The fast reads as colour before it reads as text, and a Great Feast tints
/// its whole cell — so the shape of the year is visible at a glance.
struct CalendarDayCell: View {
    let day: Day
    let onTap: () -> Void

    private var dayNumber: String {
        let trailing = String(day.date.suffix(2))
        return String(Int(trailing) ?? 0)
    }

    private var tint: Color { LiturgicalPalette.color(forToken: day.season.color) }

    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 3) {
                Text(dayNumber).font(Typography.data(13))
                Circle()
                    .fill(day.fast.isFast ? tint : .clear)
                    .frame(width: 5, height: 5)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 46)
            .background(day.rank <= 2 ? tint.opacity(0.13) : .clear,
                        in: .rect(cornerRadius: 4))
        }
        .buttonStyle(.plain)
        .accessibilityLabel(day.title.resolved(.english))
    }
}
