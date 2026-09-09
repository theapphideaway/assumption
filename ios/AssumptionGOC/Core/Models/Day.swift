import Foundation

/// One fully resolved day, exactly as the server sends it.
///
/// Nothing liturgical is computed on the client. The server owns the calendar
/// so that two native codebases can never drift apart on a rule.
struct Day: Codable, Identifiable, Sendable {
    let date: String
    let julian: String
    let pascha: String
    let paschaOffset: Int
    let languages: [ContentLanguage]
    let season: Season
    let title: LocalizedText
    let rank: Int
    let tone: Int?
    let eothinon: Int?
    let fast: Fast
    let commemorations: [Commemoration]
    let patronal: Bool
    let readings: ReadingSet?
    let icon: DayIcon?
    let parish: ParishDay

    var id: String { date }

    enum CodingKeys: String, CodingKey {
        case date, julian, pascha, languages, season, title, rank, tone
        case eothinon, fast, commemorations, patronal, readings, icon, parish
        case paschaOffset = "pascha_offset"
    }
}

struct Season: Codable, Sendable {
    let key: String
    let label: LocalizedText
    /// A design token name — "gold", "lapis", "porphyry" — not a hex value.
    /// The client maps it, so the palette can change without a server deploy.
    let color: String
}

struct Fast: Codable, Sendable {
    let level: String
    let label: LocalizedText
    let reason: LocalizedText
    let isFast: Bool

    enum CodingKeys: String, CodingKey {
        case level, label, reason
        case isFast = "is_fast"
    }
}

struct Commemoration: Codable, Identifiable, Sendable {
    let title: LocalizedText
    let rank: Int
    let kind: String
    let patronal: Bool?

    var id: String { title.resolved(.english) + kind }
}

struct DayIcon: Codable, Sendable {
    let url: String
    let credit: String?
}

struct ParishDay: Codable, Sendable {
    let services: [ServiceTime]
    let note: String?
}

struct ServiceTime: Codable, Identifiable, Sendable {
    let title: LocalizedText
    /// "18:00" — 24-hour, in the parish timezone. Formatted for display by the
    /// view model, never by the view.
    let time: String
    let location: String?
    let note: String?

    var id: String { time + title.resolved(.english) }
}
