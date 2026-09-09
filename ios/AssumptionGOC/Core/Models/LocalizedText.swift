import Foundation

/// A string in as many of the three content languages as the server holds.
///
/// The server never substitutes one language for another: an absent key means
/// the text genuinely is not on file. That distinction is preserved here — the
/// caller decides whether to fall back and the UI can mark it — because a
/// silent fallback means nobody ever notices the gap and it never gets filled.
struct LocalizedText: Codable, Hashable, Sendable {
    private let values: [String: String]

    init(_ values: [String: String]) { self.values = values }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        values = try container.decode([String: String].self)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(values)
    }

    /// The text in the requested language, or nil when it is not on file.
    func text(in language: ContentLanguage) -> String? {
        values[language.rawValue]?.nilIfBlank
    }

    /// The requested language, falling back through the others in a fixed
    /// order. Use `text(in:)` when the caller needs to know a fallback happened.
    func resolved(_ language: ContentLanguage) -> String {
        if let exact = text(in: language) { return exact }
        for candidate in ContentLanguage.allCases where candidate != language {
            if let fallback = text(in: candidate) { return fallback }
        }
        return ""
    }

    var availableLanguages: [ContentLanguage] {
        ContentLanguage.allCases.filter { values[$0.rawValue]?.nilIfBlank != nil }
    }

    func has(_ language: ContentLanguage) -> Bool {
        text(in: language) != nil
    }

    var isEmpty: Bool { availableLanguages.isEmpty }
}

private extension String {
    var nilIfBlank: String? {
        trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : self
    }
}
