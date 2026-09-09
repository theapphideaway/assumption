import SwiftUI

struct AnnouncementListView: View {
    @Environment(AppCoordinator.self) private var coordinator
    @State private var announcements: [Announcement] = []
    @State private var hasLoaded = false

    var body: some View {
        List(announcements) { announcement in
            VStack(alignment: .leading, spacing: 6) {
                if let sent = announcement.sentAt {
                    Text(sent, format: .dateTime.weekday().day().month())
                        .font(Typography.data(11))
                        .foregroundStyle(.secondary)
                }
                Text(announcement.body).font(Typography.ui(15))
            }
            .padding(.vertical, 4)
        }
        .listStyle(.plain)
        .overlay {
            if hasLoaded && announcements.isEmpty {
                ContentUnavailableView(
                    "Nothing yet",
                    systemImage: "bell",
                    description: Text("Announcements from the parish will appear here."))
            }
        }
        .navigationTitle("Announcements")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            announcements = (try? await coordinator.services.announcements.recent()) ?? []
            hasLoaded = true
        }
    }
}
