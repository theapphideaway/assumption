import Foundation

/// A message from Father to the parish.
///
/// Deliberately plain — no formatting, no attachments. The channel is valuable
/// because it is rare.
struct Announcement: Codable, Identifiable, Sendable {
    let id: Int
    let body: String
    let sentAt: Date?

    enum CodingKeys: String, CodingKey {
        case id, body
        case sentAt = "sent_at"
    }
}

struct AnnouncementPage: Codable, Sendable {
    let results: [Announcement]
}
