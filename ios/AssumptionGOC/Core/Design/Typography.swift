import SwiftUI

/// Type roles.
///
/// Liturgical text needs polytonic Greek and Church Slavonic with combining
/// marks and titlo. Bundle the faces rather than relying on the system: San
/// Francisco renders Slavonic pointing poorly, and the failure is ugly and
/// silent. Register the files in Info.plist under UIAppFonts, then set
/// `bundledFontsAvailable` to true.
enum Typography {
    static let bundledFontsAvailable = false

    private static let serifBody = "GentiumBookPlus-Regular"
    private static let serifDisplay = "EBGaramond-Regular"
    private static let slavonic = "PonomarUnicode"

    /// Prayers and scripture — long-form reading.
    static func body(_ size: CGFloat = 18, language: ContentLanguage = .english) -> Font {
        guard bundledFontsAvailable else { return .system(size: size, design: .serif) }
        return .custom(language == .slavonic ? slavonic : serifBody, size: size)
    }

    /// Feast titles and section heads.
    static func display(_ size: CGFloat = 24) -> Font {
        guard bundledFontsAvailable else { return .system(size: size, design: .serif) }
        return .custom(serifDisplay, size: size)
    }

    /// Chrome: tab bars, chips, buttons. Deliberately unliturgical so it never
    /// competes with the content.
    static func ui(_ size: CGFloat = 15, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight)
    }

    /// Dates, tones, verse numbers — anything that should align in a column.
    static func data(_ size: CGFloat = 12) -> Font {
        .system(size: size, design: .monospaced)
    }
}
