import Foundation

/// The day's prayer rule, grouped by time of day.
struct PrayerResponse: Codable, Sendable {
    let date: String
    /// The server's suggestion from the parish timezone. The client may prefer
    /// the device clock — the one deliberate exception to "clients compute
    /// nothing", safe because a time comparison cannot drift between platforms.
    let suggested: PrayerSlot
    let day: PrayerDaySummary
    let slots: [String: [PrayerDocument]]
    let scriptureEditions: [String: String]
    let missing: [MissingItem]

    enum CodingKeys: String, CodingKey {
        case date, suggested, day, slots, missing
        case scriptureEditions = "scripture_editions"
    }

    func documents(for slot: PrayerSlot) -> [PrayerDocument] {
        slots[slot.rawValue] ?? []
    }
}

enum PrayerSlot: String, Codable, CaseIterable, Identifiable, Sendable {
    case morning, hours, evening, compline

    var id: String { rawValue }

    var title: String {
        switch self {
        case .morning: "Morning"
        case .hours: "The Hours"
        case .evening: "Evening"
        case .compline: "Compline"
        }
    }

    /// Which slot the device clock suggests. The only liturgical-adjacent
    /// decision made on the client, and only because it is a clock read.
    static func forHour(_ hour: Int) -> PrayerSlot {
        switch hour {
        case 4..<11: .morning
        case 11..<17: .hours
        case 17..<22: .evening
        default: .compline
        }
    }
}

struct PrayerDaySummary: Codable, Sendable {
    let title: LocalizedText
    let fast: Fast
    let tone: Int?
    let readings: ReadingSet?
}

struct PrayerDocument: Codable, Identifiable, Sendable {
    let documentID: String
    let title: String
    let greek: String?
    let slot: PrayerSlot?
    let minutes: Int?
    let abbreviated: Bool
    let blocks: [Block]

    var id: String { documentID }

    enum CodingKeys: String, CodingKey {
        case title, greek, slot, minutes, abbreviated, blocks
        case documentID = "id"
    }
}

struct MissingItem: Codable, Identifiable, Sendable {
    let kind: String
    let reference: String?
    let slot: String?
    let why: String?

    var id: String { kind + (reference ?? slot ?? "") }

    enum CodingKeys: String, CodingKey {
        case kind = "type"
        case reference = "ref"
        case slot, why
    }
}
