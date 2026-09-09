import Foundation

/// The three content languages, which are peers rather than a base plus
/// translations. The parish has ethnic Greeks and ethnic Russians, and people
/// keep a prayer rule in the language they actually pray in.
enum ContentLanguage: String, CaseIterable, Codable, Identifiable, Sendable {
    case english = "en"
    case greek = "el"
    case slavonic = "ru"

    var id: String { rawValue }

    /// Endonym, so the picker reads naturally to the person choosing.
    var displayName: String {
        switch self {
        case .english: "English"
        case .greek: "Ἑλληνικά"
        case .slavonic: "Церковнославянский"
        }
    }

    var shortName: String {
        switch self {
        case .english: "EN"
        case .greek: "ΕΛ"
        case .slavonic: "ЦС"
        }
    }
}
