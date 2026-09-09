import SwiftUI

/// The palette, taken from an iconographer's pigment box rather than a UI kit.
///
/// The server sends a season's colour as a TOKEN NAME — "gold", "lapis" — never
/// a hex value, so the palette can be changed here without a server deploy.
enum LiturgicalPalette {
    /// Gold leaf. Pascha, the Great Feasts, every Feast of the Lord.
    static let gold = Color(red: 0.72, green: 0.54, blue: 0.18)
    /// Cinnabar. Rubrics, martyrs, the Cross. Never used for errors.
    static let cinnabar = Color(red: 0.61, green: 0.16, blue: 0.10)
    /// Lapis. Feasts of the Theotokos — and the parish's own colour, Assumption
    /// being a Dormition parish.
    static let lapis = Color(red: 0.13, green: 0.29, blue: 0.48)
    /// Imperial purple. The Triodion, Great Lent, Holy Week.
    static let porphyry = Color(red: 0.29, green: 0.15, blue: 0.26)
    /// Green earth. Pentecost, Palm Sunday, the ascetics.
    static let verte = Color(red: 0.24, green: 0.36, blue: 0.26)
    /// Great Friday.
    static let vestBlack = Color(red: 0.17, green: 0.15, blue: 0.13)

    /// Maps a server token to a colour, defaulting to gold for anything this
    /// build does not recognise — a wrong-but-dignified colour beats a crash.
    static func color(forToken token: String) -> Color {
        switch token {
        case "gold": gold
        case "cinnabar": cinnabar
        case "lapis": lapis
        case "porphyry": porphyry
        case "verte": verte
        case "black": vestBlack
        default: gold
        }
    }
}
