import SwiftUI

/// The hero of Today: the rule appointed for this hour, one tap away.
struct PrayerPromptCard: View {
    let greeting: String
    let document: PrayerDocument
    let onBegin: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(greeting.uppercased())
                .font(Typography.data(10))
                .foregroundStyle(LiturgicalPalette.lapis)

            Text(document.title)
                .font(Typography.display(23))

            if let minutes = document.minutes {
                Text("\(document.blocks.count) parts · about \(minutes) minutes")
                    .font(Typography.ui(12))
                    .foregroundStyle(.secondary)
            }

            Button(action: onBegin) {
                Text("Begin")
                    .font(Typography.ui(15, weight: .semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
            }
            .buttonStyle(.borderedProminent)
            .tint(LiturgicalPalette.lapis)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(LiturgicalPalette.lapis.opacity(0.07), in: .rect(cornerRadius: 6))
    }
}
