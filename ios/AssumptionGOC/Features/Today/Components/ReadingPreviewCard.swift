import SwiftUI

/// The day's appointed readings.
///
/// Assumption is GOARCH, so the Greek use leads. The common course reading is
/// shown beneath only where the two genuinely differ.
struct ReadingPreviewCard: View {
    let greek: [ReadingEntry]
    let common: [ReadingEntry]
    let onOpen: () -> Void

    private var primary: [ReadingEntry] { greek.isEmpty ? common : greek }
    private var showsCommonToo: Bool { !greek.isEmpty && !common.isEmpty }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("TODAY'S READINGS")
                .font(Typography.data(10))
                .foregroundStyle(.secondary)

            ForEach(primary) { entry in
                HStack(alignment: .firstTextBaseline, spacing: 8) {
                    Text(entry.source)
                        .font(Typography.ui(12))
                        .foregroundStyle(.secondary)
                        .frame(width: 62, alignment: .leading)
                    Text(entry.display)
                        .font(Typography.ui(14, weight: .medium))
                }
            }

            if showsCommonToo {
                Divider().padding(.vertical, 2)
                Text("Also appointed in the wider use")
                    .font(Typography.ui(11))
                    .foregroundStyle(.secondary)
                ForEach(common) { entry in
                    Text("\(entry.source) · \(entry.display)")
                        .font(Typography.ui(12))
                        .foregroundStyle(.secondary)
                }
            }

            Button("Read in full", action: onOpen)
                .font(Typography.ui(13, weight: .medium))
                .padding(.top, 2)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .overlay(RoundedRectangle(cornerRadius: 6).stroke(.quaternary))
    }
}
