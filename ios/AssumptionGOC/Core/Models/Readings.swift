import Foundation

/// The day's appointed readings.
///
/// Every day of the year has readings; what varies is which services carry
/// them and whether the server holds the references yet. `status` distinguishes
/// those two, so the app never implies nothing is appointed when something is.
struct ReadingSet: Codable, Sendable {
    let status: Status
    let readings: [ReadingEntry]?
    /// Convenience references for the two a parishioner looks for first.
    let gospel: String?
    let epistle: String?
    let gospelText: [Verse]?
    let epistleText: [Verse]?
    let note: String?
    let kind: String?

    enum CodingKeys: String, CodingKey {
        case status, readings, gospel, epistle, note, kind
        case gospelText = "gospel_text"
        case epistleText = "epistle_text"
    }

    enum Status: String, Codable, Sendable {
        case appointed
        case unsourced
    }

    var entries: [ReadingEntry] { readings ?? [] }
}

struct ReadingEntry: Codable, Identifiable, Sendable {
    /// "Epistle", "Gospel", "Vespers", "6th Hour", and so on.
    let source: String
    let book: String
    let display: String
    let short: String
    /// "common" or "greek". Assumption is GOARCH, so both are shown; the Greek
    /// use differs from the Slavic on a number of days.
    let tradition: String

    var id: String { source + display + tradition }
}

struct Verse: Codable, Identifiable, Sendable {
    let n: Int
    let text: LocalizedText
    let chapter: Int?

    var id: Int { n }
}
