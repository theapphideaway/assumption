import SwiftUI

struct AnnouncementCard: View {
    let announcement: Announcement
    let onOpen: () -> Void

    var body: some View {
        Button(action: onOpen) {
            VStack(alignment: .leading, spacing: 6) {
                Text("FROM THE PARISH")
                    .font(Typography.data(10))
                    .foregroundStyle(LiturgicalPalette.gold)
                Text(announcement.body)
                    .font(Typography.ui(14))
                    .multilineTextAlignment(.leading)
                    .lineLimit(3)
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(LiturgicalPalette.gold.opacity(0.08), in: .rect(cornerRadius: 6))
        }
        .buttonStyle(.plain)
        .foregroundStyle(.primary)
    }
}
