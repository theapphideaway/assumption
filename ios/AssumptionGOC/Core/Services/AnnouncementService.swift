import Foundation

protocol AnnouncementServicing: Sendable {
    func recent() async throws -> [Announcement]
}

struct AnnouncementService: AnnouncementServicing {
    private let client: APIClientProtocol

    init(client: APIClientProtocol) { self.client = client }

    func recent() async throws -> [Announcement] {
        try await client.get(.announcements, as: AnnouncementPage.self).results
    }
}
