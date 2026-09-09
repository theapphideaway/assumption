import SwiftUI

struct PrayerDocumentRow: View {
    let document: PrayerDocument
    let onOpen: () -> Void

    var body: some View {
        Button(action: onOpen) {
            VStack(alignment: .leading, spacing: 4) {
                Text(document.title)
                    .font(Typography.display(19))
                if let greek = document.greek, !greek.isEmpty {
                    Text(greek)
                        .font(Typography.ui(12))
                        .foregroundStyle(.secondary)
                }
                HStack(spacing: 6) {
                    if let minutes = document.minutes {
                        Text("about \(minutes) min")
                    }
                    if document.abbreviated {
                        Text("· abbreviated")
                    }
                }
                .font(Typography.ui(11))
                .foregroundStyle(.secondary)
            }
            .padding(.vertical, 4)
        }
        .buttonStyle(.plain)
    }
}
