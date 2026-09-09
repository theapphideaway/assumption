import Foundation

/// One node of a document.
///
/// Documents arrive as a FLAT array, never a tree: the server has already
/// spliced in shared sections, filled the day's propers and baked psalm text
/// before it reaches us. Flat means the renderer is a `ForEach` and a `switch`
/// rather than recursive views with ambiguous layout.
struct Block: Codable, Identifiable, Hashable, Sendable {
    let kind: Kind
    let text: LocalizedText?
    /// How many times a refrain is said. A number, not baked into the text, so
    /// the view decides the treatment.
    let times: Int?
    /// Verse number, for scripture.
    let number: Int?
    let chapter: Int?
    /// Psalm reference, e.g. "Ps 50".
    let reference: String?
    let tone: Int?
    /// Which edition each language's psalm text came from.
    let sources: [String: String]?

    /// Stable within a rendered document; blocks carry no server id.
    let id = UUID()

    enum CodingKeys: String, CodingKey {
        case kind = "type"
        case text, times, tone, sources, chapter
        case number = "n"
        case reference = "ref"
    }

    /// The closed set of renderable types.
    ///
    /// `unknown` is deliberate. If the server gains a type before this build
    /// does, the block renders as plain text rather than vanishing — an old app
    /// must never silently drop a line of a prayer.
    enum Kind: Hashable, Sendable {
        case heading
        case rubric
        case paragraph
        case refrain
        case hymn
        case psalm
        case verse
        case silence
        case dismissal
        case unknown(String)

        init(rawValue: String) {
            switch rawValue {
            case "heading": self = .heading
            case "rubric": self = .rubric
            case "para": self = .paragraph
            case "refrain": self = .refrain
            case "hymn": self = .hymn
            case "psalm": self = .psalm
            case "verse": self = .verse
            case "silence": self = .silence
            case "dismissal": self = .dismissal
            default: self = .unknown(rawValue)
            }
        }
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        kind = Kind(rawValue: try c.decode(String.self, forKey: .kind))
        text = try c.decodeIfPresent(LocalizedText.self, forKey: .text)
        times = try c.decodeIfPresent(Int.self, forKey: .times)
        number = try c.decodeIfPresent(Int.self, forKey: .number)
        chapter = try c.decodeIfPresent(Int.self, forKey: .chapter)
        reference = try c.decodeIfPresent(String.self, forKey: .reference)
        tone = try c.decodeIfPresent(Int.self, forKey: .tone)
        sources = try c.decodeIfPresent([String: String].self, forKey: .sources)
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encodeIfPresent(text, forKey: .text)
        try c.encodeIfPresent(times, forKey: .times)
    }

    static func == (lhs: Block, rhs: Block) -> Bool { lhs.id == rhs.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }
}
