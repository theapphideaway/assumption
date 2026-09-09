import SwiftUI

/// Everything appointed beyond the Epistle and Gospel — Vespers and Sixth Hour
/// lessons in Lent, Matins Gospels, the Passion Gospels in Holy Week.
struct OtherReadingsView: View {
    let entries: [ReadingEntry]

    private var others: [ReadingEntry] {
        entries.filter { $0.source != "Epistle" && $0.source != "Gospel" }
    }

    var body: some View {
        if !others.isEmpty {
            VStack(alignment: .leading, spacing: 8) {
                Text("ALSO APPOINTED")
                    .font(Typography.data(10))
                    .foregroundStyle(.secondary)
                ForEach(others) { entry in
                    HStack(alignment: .firstTextBaseline, spacing: 8) {
                        Text(entry.source)
                            .font(Typography.ui(12))
                            .foregroundStyle(.secondary)
                            .frame(width: 84, alignment: .leading)
                        Text(entry.display)
                            .font(Typography.ui(14))
                    }
                }
            }
            .padding(.top, 4)
        }
    }
}
